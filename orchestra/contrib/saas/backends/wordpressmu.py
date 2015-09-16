import re
import textwrap

import requests
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController
from orchestra.contrib.resources import ServiceMonitor

from .. import settings


class WordpressMuBackend(ServiceController):
    """
    Creates a wordpress site on a WordPress MultiSite installation.
    """
    verbose_name = _("Wordpress multisite")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'wordpress'"
    doc_settings = (settings,
        ('SAAS_WORDPRESS_ADMIN_PASSWORD', 'SAAS_WORDPRESS_BASE_URL')
    )
    
    def login(self, session):
        base_url = self.get_base_url()
        login_url = base_url + '/wp-login.php'
        login_data = {
            'log': 'admin',
            'pwd': settings.SAAS_WORDPRESS_ADMIN_PASSWORD,
            'redirect_to': '/wp-admin/'
        }
        response = session.post(login_url, data=login_data)
        if response.url != base_url + '/wp-admin/':
            raise IOError("Failure login to remote application")
    
    def get_base_url(self):
        base_url = settings.SAAS_WORDPRESS_BASE_URL
        return base_url.rstrip('/')
    
    def validate_response(self, response):
        if response.status_code != 200:
            errors = re.findall(r'<body id="error-page">\n\t<p>(.*)</p></body>', response.content.decode('utf8'))
            raise RuntimeError(errors[0] if errors else 'Unknown %i error' % response.status_code)
    
    def get_id(self, session, saas):
        search = self.get_base_url()
        search += '/wp-admin/network/sites.php?s=%s&action=blogs' % saas.name
        regex = re.compile(
            '<a href="http://[\.\-\w]+/wp-admin/network/site-info\.php\?id=([0-9]+)"\s+'
            'class="edit">%s</a>' % saas.name
        )
        content = session.get(search).content.decode('utf8')
        # Get id
        ids = regex.search(content)
        if not ids:
            raise RuntimeError("Blog '%s' not found" % saas.name)
        ids = ids.groups()
        if len(ids) > 1:
            raise ValueError("Multiple matches")
        # Get wpnonce
        wpnonce = re.search(r'<span class="delete">(.*)</span>', content).groups()[0]
        wpnonce = re.search(r'_wpnonce=([^"]*)"', wpnonce).groups()[0]
        return int(ids[0]), wpnonce
    
    def create_blog(self, saas, server):
        session = requests.Session()
        self.login(session)
        
        # Check if blog already exists
        try:
            self.get_id(session, saas)
        except RuntimeError:
            url = self.get_base_url()
            url += '/wp-admin/network/site-new.php'
            content = session.get(url).content.decode('utf8')
            
            wpnonce = re.compile('name="_wpnonce_add-blog"\s+value="([^"]*)"')
            wpnonce = wpnonce.search(content).groups()[0]
            
            url += '?action=add-site'
            data = {
                'blog[domain]': saas.name,
                'blog[title]': saas.name,
                'blog[email]': saas.account.email,
                '_wpnonce_add-blog': wpnonce,
            }
            
            # Validate response
            response = session.post(url, data=data)
            self.validate_response(response)
    
    def delete_blog(self, saas, server):
        session = requests.Session()
        self.login(session)
        
        try:
            id, wpnonce = self.get_id(session, saas)
        except RuntimeError:
            pass
        else:
            delete = self.get_base_url()
            delete += '/wp-admin/network/sites.php?action=confirm&action2=deleteblog'
            delete += '&id=%d&_wpnonce=%s' % (id, wpnonce)
            
            content = session.get(delete).content.decode('utf8')
            wpnonce = re.compile('name="_wpnonce"\s+value="([^"]*)"')
            wpnonce = wpnonce.search(content).groups()[0]
            data = {
                'action': 'deleteblog',
                'id': id,
                '_wpnonce': wpnonce,
                '_wp_http_referer': '/wp-admin/network/sites.php',
            }
            delete = self.get_base_url()
            delete += '/wp-admin/network/sites.php?action=deleteblog'
            response = session.post(delete, data=data)
            self.validate_response(response)
    
    def save(self, saas):
        self.append(self.create_blog, saas)
    
    def delete(self, saas):
        self.append(self.delete_blog, saas)


class WordpressMuTraffic(ServiceMonitor):
    """
    Parses apache logs,
    looking for the size of each request on the last word of the log line.
    """
    verbose_name = _("Wordpress MU Traffic")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'wordpress'"
    script_executable = '/usr/bin/python'
    monthly_sum_old_values = True
    doc_settings = (settings,
        ('SAAS_TRAFFIC_IGNORE_HOSTS', 'SAAS_WORDPRESS_LOG_PATH')
    )
    
    def prepare(self):
        access_log = settings.SAAS_WORDPRESS_LOG_PATH
        context = {
            'access_logs': str((access_log, access_log+'.1')),
            'current_date': self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'ignore_hosts': str(settings.SAAS_TRAFFIC_IGNORE_HOSTS),
        }
        self.append(textwrap.dedent("""\
            import sys
            from datetime import datetime
            from dateutil import tz
            
            def to_local_timezone(date, tzlocal=tz.tzlocal()):
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
                date = date.replace(tzinfo=tz.tzutc())
                date = date.astimezone(tzlocal)
                return date
            
            # Use local timezone
            end_date = to_local_timezone('{current_date}')
            end_date = int(end_date.strftime('%Y%m%d%H%M%S'))
            access_logs = {access_logs}
            blogs = {{}}
            months = {{
                'Jan': '01',
                'Feb': '02',
                'Mar': '03',
                'Apr': '04',
                'May': '05',
                'Jun': '06',
                'Jul': '07',
                'Aug': '08',
                'Sep': '09',
                'Oct': '10',
                'Nov': '11',
                'Dec': '12',
            }}
            
            def prepare(object_id, site_domain, ini_date):
                global blogs
                ini_date = to_local_timezone(ini_date)
                ini_date = int(ini_date.strftime('%Y%m%d%H%M%S'))
                blogs[site_domain] = [ini_date, object_id, 0]
            
            def monitor(blogs, end_date, months, access_logs):
                for access_log in access_logs:
                    try:
                        with open(access_log, 'r') as handler:
                            for line in handler.readlines():
                                meta, request, response, hostname, __ = line.split('"')
                                host, __, __, date, tz = meta.split()
                                if host in {ignore_hosts}:
                                    continue
                                try:
                                    blog = blogs[hostname]
                                except KeyError:
                                    continue
                                else:
                                    # [16/Sep/2015:11:40:38 +0200]
                                    day, month, date = date[1:].split('/')
                                    year, hour, min, sec = date.split(':')
                                    date = year + months[month] + day + hour + min + sec
                                    if blog[0] < int(date) < end_date:
                                        status, size = response.split()
                                        blog[2] += int(size)
                    except IOError as e:
                        sys.stderr.write(str(e))
                for opts in blogs.values():
                    ini_date, object_id, size = opts
                    print object_id, size
            """).format(**context)
        )
    
    def monitor(self, saas):
        context = self.get_context(saas)
        self.append("prepare(%(object_id)s, '%(site_domain)s', '%(last_date)s')" % context)
    
    def commit(self):
        self.append('monitor(blogs, end_date, months, access_logs)')
    
    def get_context(self, saas):
        return {
            'site_domain': saas.get_site_domain(),
            'last_date': self.get_last_date(saas.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
            'object_id': saas.pk,
        }
