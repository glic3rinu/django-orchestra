import textwrap
import os
import re

from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from .. import settings


class Apache2Backend(ServiceController):
    model = 'websites.Website'
    related_models = (
        ('websites.Content', 'website'),
    )
    verbose_name = _("Apache 2")
    
    def save(self, site):
        context = self.get_context(site)
        extra_conf = self.get_content_directives(site)
        if site.protocol is 'https':
            extra_conf += self.get_ssl(site)
        extra_conf += self.get_security(site)
        extra_conf += self.get_redirect(site)
        context['extra_conf'] = extra_conf
        
        apache_conf = Template(textwrap.dedent("""\
            # {{ banner }}
            <VirtualHost {{ ip }}:{{ site.port }}>
                ServerName {{ site.domains.all|first }}\
            {% if site.domains.all|slice:"1:" %}
                ServerAlias {{ site.domains.all|slice:"1:"|join:' ' }}{% endif %}
                CustomLog {{ logs }} common
                SuexecUserGroup {{ user }} {{ group }}\
            {% for line in extra_conf.splitlines %}
                {{ line | safe }}{% endfor %}
            </VirtualHost>"""
        ))
        apache_conf = apache_conf.render(Context(context))
        apache_conf += self.get_protections(site)
        context['apache_conf'] = apache_conf
        
        self.append(textwrap.dedent("""\
            {
                echo -e '%(apache_conf)s' | diff -N -I'^\s*#' %(sites_available)s -
            } || {
                echo -e '%(apache_conf)s' > %(sites_available)s
                UPDATED=1
            }""" % context
        ))
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
            method, args = content.webapp.get_directive()
            method = getattr(self, 'get_%s_directives' % method)
            directives += method(content, *args)
        return directives
    
    def get_static_directives(self, content, *args):
        context = self.get_content_context(content)
        context['path'] = args[0] % context if args else content.webapp.get_path()
        return "Alias %(location)s %(path)s\n" % context
    
    def get_fpm_directives(self, content, *args):
        context = self.get_content_context(content)
        context['fcgi_path'] = args[0] % context
        directive = "ProxyPassMatch ^%(location)s(.*\.php(/.*)?)$ %(fcgi_path)s$1\n"
        return directive % context
    
    def get_fcgi_directives(self, content, fcgid_path):
        context = self.get_content_context(content)
        context['fcgid_path'] = fcgid_path % context
        fcgid = self.get_static_directives(content)
        fcgid += textwrap.dedent("""\
            ProxyPass %(location)s !
            <Directory %(app_path)s>
                Options +ExecCGI
                AddHandler fcgid-script .php
                FcgidWrapper %(fcgid_path)s\
            """ % context)
        for option in content.webapp.options.filter(name__startswith='Fcgid'):
            fcgid += "    %s %s\n" % (option.name, option.value)
        fcgid += "</Directory>\n"
        return fcgid
    
    def get_ssl(self, site):
        cert = settings.WEBSITES_DEFAULT_HTTPS_CERT
        custom_cert = site.options.filter(name='ssl')
        if custom_cert:
            cert = tuple(custom_cert[0].value.split())
        # TODO separate directtives?
        directives = textwrap.dedent("""\
            SSLEngine on
            SSLCertificateFile %s
            SSLCertificateKeyFile %s\
            """ % cert
        )
        return directives
    
    def get_security(self, site):
        directives = ''
        for rules in site.options.filter(name='sec_rule_remove'):
            for rule in rules.value.split():
                directives += "SecRuleRemoveById %i\n" % int(rule)
        for modsecurity in site.options.filter(name='sec_rule_off'):
            directives += textwrap.dedent("""\
                <LocationMatch %s>
                    SecRuleEngine Off
                </LocationMatch>\
                """ % modsecurity.value)
        if directives:
            directives = '<IfModule mod_security2.c>\n%s\n</IfModule>' % directives
        return directives
    
    def get_redirect(self, site):
        directives = ''
        for redirect in site.options.filter(name='redirect'):
            if re.match(r'^.*[\^\*\$\?\)]+.*$', redirect.value):
                directives += "RedirectMatch %s" % redirect.value
            else:
                directives += "Redirect %s" % redirect.value
        return directives
    
    def get_protections(self, site):
        protections = ""
        __, regex = settings.WEBSITES_OPTIONS['directory_protection']
        context = self.get_context(site)
        for protection in site.options.filter(name='directory_protection'):
            path, name, passwd = re.match(regex, protection.value).groups()
            path = os.path.join(context['root'], path)
            passwd = os.path.join(self.USER_HOME % context, passwd)
            protections += textwrap.dedent("""
                <Directory %s>
                    AllowOverride All
                    #AuthPAM_Enabled off
                    AuthType Basic
                    AuthName %s
                    AuthUserFile %s
                    <Limit GET POST>
                        require valid-user
                    </Limit>
                </Directory>""" % (path, name, passwd)
            )
        return protections
    
    def enable_or_disable(self, site):
        context = self.get_context(site)
        self.append("ls -l %(sites_enabled)s > /dev/null; DISABLED=$?" % context)
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
            'ip': settings.WEBSITES_DEFAULT_IP,
            'site_unique_name': site.unique_name,
            'user': site.get_username(),
            'group': site.get_groupname(),
            'sites_enabled': sites_enabled,
            'sites_available': "%s.conf" % os.path.join(sites_available, site.unique_name),
            'logs': site.get_www_log_path(),
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
    
    def prepare(self):
        current_date = self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z")
        self.append(textwrap.dedent("""\
            function monitor () {
                OBJECT_ID=$1
                INI_DATE=$2
                LOG_FILE="$3"
                {
                    awk -v ini="${INI_DATE}" -v end="$(date '+%%Y%%m%%d%%H%%M%%S' -d '%s')" '
                    BEGIN {
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
                    }' "${LOG_FILE}" || echo 0
                } | xargs echo ${OBJECT_ID}
            }""" % current_date))
    
    def monitor(self, site):
        context = self.get_context(site)
        self.append('monitor {object_id} $(date "+%Y%m%d%H%M%S" -d "{last_date}") "{log_file}"'.format(**context))
    
    def get_context(self, site):
        return {
            'log_file': '%s{,.1}' % site.get_www_log_path(),
            'last_date': self.get_last_date(site.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
            'object_id': site.pk,
        }
