import os
import re
import textwrap

from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from .. import settings
from ..utils import normurlpath


class Apache2Backend(ServiceController):
    HTTP_PORT = 80
    HTTPS_PORT = 443
    
    model = 'websites.Website'
    related_models = (
        ('websites.Content', 'website'),
    )
    verbose_name = _("Apache 2")
    
    def render_virtual_host(self, site, context, ssl=False):
        context['port'] = self.HTTPS_PORT if ssl else self.HTTP_PORT
        extra_conf = self.get_content_directives(site)
        directives = site.get_directives()
        if ssl:
            extra_conf += self.get_ssl(directives)
        extra_conf += self.get_security(directives)
        extra_conf += self.get_redirects(directives)
        extra_conf += self.get_proxies(directives)
        extra_conf += self.get_saas(directives)
        settings_context = site.get_settings_context()
        for location, directive in settings.WEBSITES_VHOST_EXTRA_DIRECTIVES:
            extra_conf.append((location, directive % settings_context))
        # Order extra conf directives based on directives (longer first)
        extra_conf = sorted(extra_conf, key=lambda a: len(a[0]), reverse=True)
        context['extra_conf'] = '\n'.join([conf for location, conf in extra_conf])
        return Template(textwrap.dedent("""\
            <VirtualHost {{ ip }}:{{ port }}>
                ServerName {{ site.domains.all|first }}\
            {% if site.domains.all|slice:"1:" %}
                ServerAlias {{ site.domains.all|slice:"1:"|join:' ' }}{% endif %}\
            {% if access_log %}
                CustomLog {{ access_log }} common{% endif %}\
            {% if error_log %}
                ErrorLog {{ error_log }}{% endif %}
                SuexecUserGroup {{ user }} {{ group }}\
            {% for line in extra_conf.splitlines %}
                {{ line | safe }}{% endfor %}
                IncludeOptional /etc/apache2/extra-vhos[t]/{{ site_unique_name }}.con[f]
            </VirtualHost>
            """)
        ).render(Context(context))
    
    def render_redirect_https(self, context):
        context['port'] = self.HTTP_PORT
        return Template(textwrap.dedent("""
            <VirtualHost {{ ip }}:{{ port }}>
                ServerName {{ site.domains.all|first }}\
            {% if site.domains.all|slice:"1:" %}
                ServerAlias {{ site.domains.all|slice:"1:"|join:' ' }}{% endif %}\
            {% if access_log %}
                CustomLog {{ access_log }} common{% endif %}\
            {% if error_log %}
                ErrorLog {{ error_log }}{% endif %}
                RewriteEngine On
                RewriteCond %{HTTPS} off
                RewriteRule (.*) https://%{HTTP_HOST}%{REQUEST_URI}
            </VirtualHost>
            """)
        ).render(Context(context))
    
    def save(self, site):
        context = self.get_context(site)
        apache_conf = '# %(banner)s\n' % context
        if site.protocol in (site.HTTP, site.HTTP_AND_HTTPS):
            apache_conf += self.render_virtual_host(site, context, ssl=False)
        if site.protocol in (site.HTTP_AND_HTTPS, site.HTTPS_ONLY, site.HTTPS):
            apache_conf += self.render_virtual_host(site, context, ssl=True)
        if site.protocol == site.HTTPS_ONLY:
            apache_conf += self.render_redirect_https(context)
        context['apache_conf'] = apache_conf
        self.append(textwrap.dedent("""\
            apache_conf='%(apache_conf)s'
            {
                echo -e "${apache_conf}" | diff -N -I'^\s*#' %(sites_available)s -
            } || {
                echo -e "${apache_conf}" > %(sites_available)s
                UPDATED=1
            }""") % context
        )
        self.enable_or_disable(site)
    
    def delete(self, site):
        context = self.get_context(site)
        self.append("a2dissite %(site_unique_name)s.conf && UPDATED=1" % context)
        self.append("rm -fr %(sites_available)s" % context)
    
    def commit(self):
        """ reload Apache2 if necessary """
        self.append('if [[ $UPDATED == 1 ]]; then service apache2 reload; fi')
    
    def get_directives(self, directive, context):
        method, args = directive[0], directive[1:]
        try:
            method = getattr(self, 'get_%s_directives' % method)
        except AttributeError:
            raise AttributeError("%s does not has suport for '%s' directive." %
                    (self.__class__.__name__, method))
        return method(context, *args)
    
    def get_content_directives(self, site):
        directives = []
        for content in site.content_set.all():
            directive = content.webapp.get_directive()
            context = self.get_content_context(content)
            directives += self.get_directives(directive, context)
        return directives
    
    def get_static_directives(self, context, app_path):
        context['app_path'] = os.path.normpath(app_path % context)
        location = "%(location)s/" % context
        directive = "Alias %(location)s/ %(app_path)s/" % context
        return [(location, directive)]
    
    def get_fpm_directives(self, context, socket, app_path):
        if ':' in socket:
            # TCP socket
            target = 'fcgi://%(socket)s%(app_path)s/$1'
        else:
            # UNIX socket
            target = 'unix:%(socket)s|fcgi://127.0.0.1%(app_path)s/'
            if context['location']:
                target = 'unix:%(socket)s|fcgi://127.0.0.1%(app_path)s/$1'
        context.update({
            'app_path': os.path.normpath(app_path),
            'socket': socket,
        })
        location = "%(location)s/" % context
        directives = textwrap.dedent("""\
            ProxyPassMatch ^%(location)s/(.*\.php(/.*)?)$ {target}
            Alias %(location)s/ %(app_path)s/""".format(target=target) % context
        )
        return [(location, directives)]
    
    def get_fcgid_directives(self, context, app_path, wrapper_path):
        context.update({
            'app_path': os.path.normpath(app_path),
            'wrapper_path': wrapper_path,
        })
        location = "%(location)s/" % context
        directives = textwrap.dedent("""\
            Alias %(location)s/ %(app_path)s/
            ProxyPass %(location)s/ !
            <Directory %(app_path)s/>
                Options +ExecCGI
                AddHandler fcgid-script .php
                FcgidWrapper %(wrapper_path)s
            </Directory>""") % context
        return [(location, directives)]
    
    def get_ssl(self, directives):
        cert = directives.get('ssl_cert')
        key = directives.get('ssl_key')
        ca = directives.get('ssl_ca')
        if not (cert and key):
            cert = [settings.WEBSITES_DEFAULT_SSL_CERT]
            key = [settings.WEBSITES_DEFAULT_SSL_KEY]
            ca = [settings.WEBSITES_DEFAULT_SSL_CA]
            if not (cert and key):
                return []
        config = 'SSLEngine on\n'
        config += "SSLCertificateFile %s\n" % cert[0]
        config += "SSLCertificateKeyFile %s\n" % key[0]
        if ca:
           config += "SSLCACertificateFile %s\n" % ca[0]
        return [('', config)]
        
    def get_security(self, directives):
        security = []
        for rules in directives.get('sec_rule_remove', []):
            for rule in rules.value.split():
                sec_rule = "SecRuleRemoveById %i" % int(rule)
                security.append(('', sec_rule))
        for location in directives.get('sec_engine', []):
            sec_rule = textwrap.dedent("""\
                <Location %s>
                    SecRuleEngine off
                </Location>""") % location
            security.append((location, sec_rule))
        return security
    
    def get_redirects(self, directives):
        redirects = []
        for redirect in directives.get('redirect', []):
            location, target = redirect.split()
            if re.match(r'^.*[\^\*\$\?\)]+.*$', redirect):
                redirect = "RedirectMatch %s %s" % (location, target)
            else:
                redirect = "Redirect %s %s" % (location, target)
            redirects.append((location, redirect))
        return redirects
    
    def get_proxies(self, directives):
        proxies = []
        for proxy in directives.get('proxy', []):
            location, target = proxy.split()
            location = normurlpath(source)
            proxy = textwrap.dedent("""\
                ProxyPass {location} {target}
                ProxyPassReverse {location} {target}""".format(
                    location=location, target=target)
            )
            proxies.append((location, proxy))
        return proxies
    
    def get_saas(self, directives):
        saas = []
        for name, values in directives.iteritems():
            if name.endswith('-saas'):
                for value in values:
                    context = {
                        'location': normurlpath(value),
                    }
                    directive = settings.WEBSITES_SAAS_DIRECTIVES[name]
                    saas += self.get_directives(directive, context)
        return saas
#    def get_protections(self, site):
#        protections = ''
#        context = self.get_context(site)
#        for protection in site.directives.filter(name='directory_protection'):
#            path, name, passwd = protection.value.split()
#            path = os.path.join(context['root'], path)
#            passwd = os.path.join(self.USER_HOME % context, passwd)
#            protections += textwrap.dedent("""
#                <Directory %s>
#                    AllowOverride All
#                    #AuthPAM_Enabled off
#                    AuthType Basic
#                    AuthName %s
#                    AuthUserFile %s
#                    <Limit GET POST>
#                        require valid-user
#                    </Limit>
#                </Directory>""" % (path, name, passwd)
#            )
#        return protections
    
    def enable_or_disable(self, site):
        context = self.get_context(site)
        if site.is_active:
            self.append(textwrap.dedent("""\
                if [[ ! -f %(sites_enabled)s ]]; then
                    a2ensite %(site_unique_name)s.conf
                    UPDATED=1
                fi""") % context
            )
        else:
            self.append(textwrap.dedent("""\
                if [[ -f %(sites_enabled)s ]]; then
                    a2dissite %(site_unique_name)s.conf;
                    UPDATED=1
                fi""") % context
            )
    
    def get_username(self, site):
        option = site.get_directives().get('user_group')
        if option:
            return option[0]
        return site.get_username()
    
    def get_groupname(self, site):
        option = site.get_directives().get('user_group')
        if option and ' ' in option:
            user, group = option.split()
            return group
        return site.get_groupname()
    
    def get_context(self, site):
        base_apache_conf = settings.WEBSITES_BASE_APACHE_CONF
        sites_available = os.path.join(base_apache_conf, 'sites-available')
        sites_enabled = os.path.join(base_apache_conf, 'sites-enabled')
        context = {
            'site': site,
            'site_name': site.name,
            'ip': settings.WEBSITES_DEFAULT_IP,
            'site_unique_name': site.unique_name,
            'user': self.get_username(site),
            'group': self.get_groupname(site),
            # TODO remove '0-'
            'sites_enabled': "%s.conf" % os.path.join(sites_enabled, '0-'+site.unique_name),
            'sites_available': "%s.conf" % os.path.join(sites_available, site.unique_name),
            'access_log': site.get_www_access_log_path(),
            'error_log': site.get_www_error_log_path(),
            'banner': self.get_banner(),
        }
        return context
    
    def get_content_context(self, content):
        context = self.get_context(content.website)
        context.update({
            'type': content.webapp.type,
            'location': normurlpath(content.path),
            'app_name': content.webapp.name,
            'app_path': content.webapp.get_path(),
        })
        return context


class Apache2Traffic(ServiceMonitor):
    model = 'websites.Website'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _("Apache 2 Traffic")
    
    def prepare(self):
        super(Apache2Traffic, self).prepare()
        ignore_hosts = '\\|'.join(settings.WEBSITES_TRAFFIC_IGNORE_HOSTS)
        context = {
            'current_date': self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'ignore_hosts': '-v "%s"' % ignore_hosts if ignore_hosts else '',
        }
        self.append(textwrap.dedent("""\
            function monitor () {
                OBJECT_ID=$1
                INI_DATE=$(date "+%%Y%%m%%d%%H%%M%%S" -d "$2")
                END_DATE=$(date '+%%Y%%m%%d%%H%%M%%S' -d '%(current_date)s')
                LOG_FILE="$3"
                {
                    { grep %(ignore_hosts)s ${LOG_FILE} || echo -e '\\r'; } \\
                        | awk -v ini="${INI_DATE}" -v end="${END_DATE}" '
                            BEGIN {
                                sum = 0
                                months["Jan"] = "01"
                                months["Feb"] = "02"
                                months["Mar"] = "03"
                                months["Apr"] = "04"
                                months["May"] = "05"
                                months["Jun"] = "06"
                                months["Jul"] = "07"
                                months["Aug"] = "08"
                                months["Sep"] = "09"
                                months["Oct"] = "10"
                                months["Nov"] = "11"
                                months["Dec"] = "12"
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
                            }' || [[ $? == 1 ]] && true
                } | xargs echo ${OBJECT_ID}
            }""") % context)
    
    def monitor(self, site):
        context = self.get_context(site)
        self.append('monitor {object_id} "{last_date}" {log_file}'.format(**context))
    
    def get_context(self, site):
        return {
            'log_file': '%s{,.1}' % site.get_www_access_log_path(),
            'last_date': self.get_last_date(site.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
            'object_id': site.pk,
        }
