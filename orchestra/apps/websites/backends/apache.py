import os

from django.template import Template, Context
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from .. import settings


class Apache2Backend(ServiceController):
    model = 'websites.Website'
    related_models = (('websites.Content', 'website'),)
    verbose_name = _("Apache 2")
    
    def save(self, site):
        context = self.get_context(site)
        extra_conf = self.get_content_directives(site)
        if site.protocol is 'https':
            extra_conf += self.get_ssl(site)
        extra_conf += self.get_security(site)
        context['extra_conf'] = extra_conf
        
        apache_conf = Template(
            "# {{ banner }}\n"
            "<VirtualHost *:{{ site.port }}>\n"
            "    ServerName {{ site.domains.all|first }}\n"
            "{% if site.domains.all|slice:\"1:\" %}"
            "    ServerAlias {{ site.domains.all|slice:\"1:\"|join:' ' }}\n"
            "{% endif %}"
            "    CustomLog {{ logs }} common\n"
            "    SuexecUserGroup {{ user }} {{ group }}\n"
            "{% for line in extra_conf.splitlines %}"
            "    {{ line | safe }}\n"
            "{% endfor %}"
            "</VirtualHost>\n"
        )
        apache_conf = apache_conf.render(Context(context))
        apache_conf += self.get_protections(site)
        context['apache_conf'] = apache_conf
        
        self.append(
            "{ echo -e '%(apache_conf)s' | diff -N -I'^\s*#' %(sites_available)s - ; } ||"
            "  { echo -e '%(apache_conf)s' > %(sites_available)s; UPDATED=1; }" % context
        )
        self.enable_or_disable(site)
    
    def delete(self, site):
        context = self.get_context(site)
        self.append("a2dissite %(site_unique_name)s.conf && UPDATED=1" % context)
        self.append("rm -fr %(sites_available)s" % context)
    
    def commit(self):
        """ reload Apache2 if necessary """
        self.append('[[ $UPDATED == 1 ]] && service apache2 reload')
    
    def get_content_directives(self, site):
        directives = ''
        for content in site.content_set.all().order_by('-path'):
            method, args = content.webapp.get_method()
            method = getattr(self, 'get_%s_directives' % method)
            directives += method(content, *args)
        return directives
    
    def get_alias_directives(self, content, *args):
        context = self.get_content_context(content)
        context['path'] = args[0] % context if args else content.webapp.get_path()
        return "Alias %(location)s %(path)s\n" % context
    
    def get_fpm_directives(self, content, *args):
        context = self.get_content_context(content)
        context['fcgi_path'] = args[0] % context
        directive = "ProxyPassMatch ^%(location)s(.*\.php(/.*)?)$ %(fcgi_path)s$1\n"
        return directive % context
    
    def get_fcgid_directives(self, content, fcgid_path):
        context = self.get_content_context(content)
        context['fcgid_path'] = fcgid_path % context
        fcgid = self.get_alias_directives(content)
        fcgid += (
            "ProxyPass %(location)s !\n"
            "<Directory %(app_path)s>\n"
            "    Options +ExecCGI\n"
            "    AddHandler fcgid-script .php\n"
            "    FcgidWrapper %(fcgid_path)s\n"
        ) % context
        for option in content.webapp.options.filter(name__startswith='Fcgid'):
            fcgid += "    %s %s\n" % (option.name, option.value)
        fcgid += "</Directory>\n"
        return fcgid
    
    def get_ssl(self, site):
        cert = settings.WEBSITES_DEFAULT_HTTPS_CERT
        custom_cert = site.options.filter(name='ssl')
        if custom_cert:
            cert = tuple(custom_cert[0].value.split())
        directives = (
            "SSLEngine on\n"
            "SSLCertificateFile %s\n"
            "SSLCertificateKeyFile %s\n"
        ) % cert
        return directives
    
    def get_security(self, site):
        directives = ''
        for rules in site.options.filter(name='sec_rule_remove'):
            for rule in rules.split():
                directives += "SecRuleRemoveById %d" % rule
        
        for modsecurity in site.options.filter(name='sec_rule_off'):
            directives += (
                "<LocationMatch %s>\n"
                "    SecRuleEngine Off\n"
                "</LocationMatch>\n" % modsecurity.value
            )
        return directives
    
    def get_protections(self, site):
        protections = ""
        __, regex = settings.WEBSITES_OPTIONS['directory_protection']
        for protection in site.options.filter(name='directory_protection'):
            path, name, passwd = re.match(regex, protection.value).groups()
            path = os.path.join(context['root'], path)
            passwd = os.path.join(self.USER_HOME % context, passwd)
            protections += ("\n"
                "<Directory %s>\n"
                "    AllowOverride All\n"
#                "    AuthPAM_Enabled off\n"
                "    AuthType Basic\n"
                "    AuthName %s\n"
                "    AuthUserFile %s\n"
                "    <Limit GET POST>\n"
                "        require valid-user\n"
                "    </Limit>\n"
                "</Directory>\n" % (path, name, passwd)
            )
        return protections
    
    def enable_or_disable(self, site):
        context = self.get_context(site)
        self.append("ls -l %(sites_enabled)s; DISABLED=$?" % context)
        if site.is_active:
            self.append("if [[ $DISABLED ]]; then a2ensite %(site_unique_name)s.conf;\n"
                        "else UPDATED=0; fi" % context)
        else:
            self.append("if [[ ! $DISABLED ]]; then a2dissite %(site_unique_name)s.conf;\n"
                        "else UPDATED=0; fi" % context)
    
    def get_context(self, site):
        base_apache_conf = settings.WEBSITES_BASE_APACHE_CONF
        sites_available = os.path.join(base_apache_conf, 'sites-available')
        sites_enabled = os.path.join(base_apache_conf, 'sites-enabled')
        context = {
            'site': site,
            'site_name': site.name,
            'site_unique_name': site.unique_name,
            'user': site.account.user.username,
            'group': site.account.user.username,
            'sites_enabled': sites_enabled,
            'sites_available': "%s.conf" % os.path.join(sites_available, site.unique_name),
            'logs': os.path.join(settings.WEBSITES_BASE_APACHE_LOGS, site.unique_name),
            'banner': self.get_banner(),
        }
        return context
    
    def get_content_context(self, content):
        context = self.get_context(content.website)
        context.update({
            'type': content.webapp.type,
            'location': content.path,
            'app_name': content.webapp.name,
            'app_path': content.webapp.get_path(),
            'fpm_port': content.webapp.get_fpm_port(),
        })
        return context


class Apache2Traffic(ServiceMonitor):
    model = 'websites.Website'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _("Apache 2 Traffic")
    
    def monitor(self, site):
        context = self.get_context(site)
        self.append("""{
            awk 'BEGIN {
                ini = "%(last_date)s"
                end = "%(current_date)s"
                sum = 0
                
                months["Jan"] = "01";
                months["Feb"] = "02";
                months["Mar"] = "03";
                months["Apr"] = "04";
                months["May"] = "05";
                months["Jun"] = "06";
                months["Jul"] = "07";
                months["Aug"] = "08";
                months["Sep"] = "09";
                months["Oct"] = "10";
                months["Nov"] = "11";
                months["Dec"] = "12";
            } {
                # date = [11/Jul/2014:13:50:41
                date = substr($4, 2)
                year = substr(date, 8, 4)
                month = months[substr(date, 4, 3)];
                day = substr(date, 1, 2)
                hour = substr(date, 13, 2)
                minute = substr(date, 16, 2)
                second = substr(date, 19, 2)
                line_date = year month day hour minute second
                if ( line_date > ini && line_date < end)
                    sum += $NF
            } END {
                print sum
            }' %(log_file)s || echo 0; } | xargs echo %(object_id)s """ % context)
    
    def get_context(self, site):
        last_date = timezone.localtime(self.get_last_date(site.pk))
        current_date = timezone.localtime(self.current_date)
        return {
            'log_file': os.path.join(settings.WEBSITES_BASE_APACHE_LOGS, site.unique_name),
            'last_date': last_date.strftime("%Y%m%d%H%M%S"),
            'current_date': current_date.strftime("%Y%m%d%H%M%S"),
            'object_id': site.pk,
        }
