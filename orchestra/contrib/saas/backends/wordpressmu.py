import re
import sys
import textwrap
import time
from functools import partial
from urllib.parse import urlparse

import requests
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController

from . import ApacheTrafficByHost
from .. import settings


class WordpressMuController(ServiceController):
    """
    Creates a wordpress site on a WordPress MultiSite installation.
    
    You should point it to the database server
    """
    verbose_name = _("Wordpress multisite")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'wordpress'"
    doc_settings = (settings,
        ('SAAS_WORDPRESS_ADMIN_PASSWORD', 'SAAS_WORDPRESS_MAIN_URL', 'SAAS_WORDPRESS_VERIFY_SSL')
    )
    VERIFY = settings.SAAS_WORDPRESS_VERIFY_SSL
    
    def with_retry(self, method, *args, retries=1, sleep=0.5, **kwargs):
        for i in range(retries):
            try:
                return method(*args, verify=self.VERIFY, **kwargs)
            except requests.exceptions.ConnectionError:
                if i >= retries:
                    raise
                sys.stderr.write("Connection error while {method}{args}, retry {i}/{retries}\n".format(
                    method=method.__name__, args=str(args), i=i, retries=retries))
                time.sleep(sleep)
    
    def login(self, session):
        main_url = self.get_main_url()
        login_url = main_url + '/wp-login.php'
        login_data = {
            'log': 'admin',
            'pwd': settings.SAAS_WORDPRESS_ADMIN_PASSWORD,
            'redirect_to': '/wp-admin/'
        }
        sys.stdout.write("Login URL: %s\n" % login_url)
        response = self.with_retry(session.post, login_url, data=login_data)
        if response.url != main_url + '/wp-admin/':
            raise IOError("Failure login to remote application (%s)" % login_url)
    
    def get_main_url(self):
        main_url = settings.SAAS_WORDPRESS_MAIN_URL
        return main_url.rstrip('/')
    
    def validate_response(self, response):
        if response.status_code != 200:
            content = response.content.decode('utf8')
            errors = re.findall(r'<body id="error-page">\n\t<p>(.*)</p></body>', content)
            raise RuntimeError(errors[0] if errors else 'Unknown %i error' % response.status_code)
    
    def get_id(self, session, saas):
        blog_id = saas.data.get('blog_id')
        search = self.get_main_url()
        search += '/wp-admin/network/sites.php?s=%s&action=blogs' % saas.name
        regex = re.compile(
            '<a href="http://[\.\-\w]+/wp-admin/network/site-info\.php\?id=([0-9]+)"\s+'
            'class="edit">%s</a>' % saas.name
        )
        sys.stdout.write("Search URL: %s\n" % search)
        response = self.with_retry(session.get, search)
        content = response.content.decode('utf8')
        # Get id
        ids = regex.search(content)
        if not ids and not blog_id:
            raise RuntimeError("Blog '%s' not found" % saas.name)
        if ids:
            ids = ids.groups()
            if len(ids) > 1 and not blog_id:
                raise ValueError("Multiple matches")
        return blog_id or int(ids[0]), content
    
    def create_blog(self, saas, server):
        if saas.data.get('blog_id'):
            return
        
        session = requests.Session()
        self.login(session)
        
        # Check if blog already exists
        try:
            blog_id, content = self.get_id(session, saas)
        except RuntimeError:
            url = self.get_main_url()
            url += '/wp-admin/network/site-new.php'
            sys.stdout.write("Create URL: %s\n" % url)
            content = self.with_retry(session.get, url).content.decode('utf8')
            
            wpnonce = re.compile('name="_wpnonce_add-blog"\s+value="([^"]*)"')
            try:
                wpnonce = wpnonce.search(content).groups()[0]
            except AttributeError:
                raise RuntimeError("wpnonce not foud in %s" % content)
            
            url += '?action=add-site'
            data = {
                'blog[domain]': saas.name,
                'blog[title]': saas.name,
                'blog[email]': saas.account.email,
                '_wpnonce_add-blog': wpnonce,
            }
            
            # Validate response
            response = self.with_retry(session.post, url, data=data)
            self.validate_response(response)
            blog_id = re.compile(r'<link id="wp-admin-canonical" rel="canonical" href="http(?:[^ ]+)/wp-admin/network/site-new.php\?id=([0-9]+)" />')
            content = response.content.decode('utf8')
            blog_id = blog_id.search(content).groups()[0]
            sys.stdout.write("Created blog ID: %s\n" % blog_id)
            saas.data['blog_id'] = int(blog_id)
            saas.save(update_fields=('data',))
            return True
        else:
            sys.stdout.write("Retrieved blog ID: %s\n" % blog_id)
            saas.data['blog_id'] = int(blog_id)
            saas.save(update_fields=('data',))
    
    def do_action(self, action, session, id, content, saas):
        url_regex = r"""<span class=["']+%s["']+><a href=["']([^>]*)['"]>""" % action
        action_url = re.search(url_regex, content).groups()[0].replace("&#038;", '&')
        sys.stdout.write("%s confirm URL: %s\n" % (action, action_url))
        
        content = self.with_retry(session.get, action_url).content.decode('utf8')
        wpnonce = re.compile('name="_wpnonce"\s+value="([^"]*)"')
        try:
            wpnonce = wpnonce.search(content).groups()[0]
        except AttributeError:
            raise RuntimeError(re.search(r'<body id="error-page">([^<]+)<', content).groups()[0])
        data = {
            'action': action,
            'id': id,
            '_wpnonce': wpnonce,
            '_wp_http_referer': '/wp-admin/network/sites.php',
        }
        action_url = self.get_main_url()
        action_url += '/wp-admin/network/sites.php?action=%sblog' % action
        sys.stdout.write("%s URL: %s\n" % (action, action_url))
        response = self.with_retry(session.post, action_url, data=data)
        self.validate_response(response)
    
    def is_active(self, content):
        return bool(
            re.findall(r"""<span class=["']deactivate['"]""", content) and
            not re.findall(r"""<span class=["']activate['"]""", content)
        )
    
    def activate(self, saas, server):
        session = requests.Session()
        self.login(session)
        try:
            id, content = self.get_id(session, saas)
        except RuntimeError:
            pass
        else:
            if not self.is_active(content):
                return self.do_action('activate', session, id, content, saas)
    
    def deactivate(self, saas, server):
        session = requests.Session()
        self.login(session)
        try:
            id, content = self.get_id(session, saas)
        except RuntimeError:
            pass
        else:
            if self.is_active(content):
                return self.do_action('deactivate', session, id, content, saas)
    
    def save(self, saas):
        created = self.append(self.create_blog, saas)
        if saas.active and not created:
            self.append(self.activate, saas)
        else:
            self.append(self.deactivate, saas)
        context = self.get_context(saas)
        context['IDENT'] =  "b.domain = '%(domain)s'" % context
        if context['blog_id']:
            context['IDENT'] =  "b.blog_id = '%(blog_id)s'" % context
        self.append(textwrap.dedent("""
            # Update custom URL mapping
            existing=( $(mysql -Nrs %(db_name)s --execute="
                SELECT b.blog_id, b.domain, m.domain, b.path
                    FROM wp_domain_mapping AS m, wp_blogs AS b
                    WHERE m.blog_id = b.blog_id AND m.active AND %(IDENT)s;") )
            if [[ ${existing[0]} != "" ]]; then
                echo "Existing blog with ID ${existing[0]}"
                # Clear custom domain
                if [[ "%(custom_domain)s" == "" ]]; then
                    mysql %(db_name)s --execute="
                        DELETE FROM m
                            USING wp_domain_mapping AS m, wp_blogs AS b
                            WHERE m.blog_id = b.blog_id AND m.active AND %(IDENT)s;
                        UPDATE wp_blogs
                            SET path='/'
                            WHERE blog_id = ${existing[0]};"
                elif [[ "${existing[2]}" != "%(custom_domain)s" || "${existing[3]}" != "%(custom_path)s" ]]; then
                    mysql %(db_name)s --execute="
                        UPDATE wp_domain_mapping as m, wp_blogs as b
                            SET m.domain = '%(custom_domain)s', b.path = '%(custom_path)s'
                            WHERE m.blog_id = b.blog_id AND m.active AND %(IDENT)s;"
                fi
            elif [[ "%(custom_domain)s" != "" ]]; then
                echo "Non existing blog with custom domain %(domain)s"
                blog=( $(mysql -Nrs %(db_name)s --execute="
                    SELECT blog_id, path
                        FROM wp_blogs
                        WHERE domain = '%(domain)s';") )
                if [[ "${blog[0]}" != "" ]]; then
                    echo "Blog %(domain)s found, ID: ${blog[0]}"
                    mysql %(db_name)s --execute="
                        UPDATE wp_domain_mapping
                            SET active = 0
                            WHERE active AND blog_id = ${blog[0]};
                        INSERT INTO wp_domain_mapping
                            (blog_id, domain, active) VALUES (${blog[0]}, '%(custom_domain)s', 1);"
                    if [[ "${blog[1]}" != "%(custom_path)s" ]]; then
                        mysql %(db_name)s --execute="
                            UPDATE wp_blogs
                                SET path = '%(custom_path)s'
                                WHERE blog_id = ${blog[0]};"
                    fi
                else
                    echo "Blog %(domain)s not found"
                fi
            fi""") % context
        )
    
    def delete_blog(self, saas, server):
        session = requests.Session()
        self.login(session)
        try:
            id, content = self.get_id(session, saas)
        except RuntimeError:
            pass
        else:
            return self.do_action('delete', session, id, content, saas)
    
    def delete(self, saas):
        self.append(self.delete_blog, saas)
    
    def get_context(self, saas):
        domain = saas.get_site_domain()
        context = {
            'db_name': settings.SAAS_WORDPRESS_DB_NAME,
            'domain': domain,
            'custom_domain': '',
            'custom_path': '/',
            'blog_id': saas.data.get('blog_id', ''),
        }
        if saas.custom_url:
            custom_url = urlparse(saas.custom_url)
            context.update({
                'custom_domain': custom_url.netloc,
                'custom_path': custom_url.path,
            })
        return context


class WordpressMuTraffic(ApacheTrafficByHost):
    __doc__ = ApacheTrafficByHost.__doc__
    verbose_name = _("Wordpress MU Traffic")
    default_route_match = "saas.service == 'wordpress'"
    doc_settings = (settings,
        ('SAAS_TRAFFIC_IGNORE_HOSTS', 'SAAS_WORDPRESS_LOG_PATH')
    )
    log_path = settings.SAAS_WORDPRESS_LOG_PATH
