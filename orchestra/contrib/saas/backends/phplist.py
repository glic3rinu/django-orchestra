import hashlib
import re
import sys
import textwrap

import requests
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController
from orchestra.contrib.resources import ServiceMonitor
from orchestra.utils.sys import sshrun

from .. import settings


class PhpListSaaSController(ServiceController):
    """
    Creates a new phplist instance on a phpList multisite installation.
    The site is created by means of creating a new database per phpList site,
    but all sites share the same code.
    
    Different databases are used instead of prefixes because php-list reacts by launching
    the installation process.
    
    <tt>// config/config.php
    $site = getenv("SITE");
    if ( $site == '' ) {
        $site = array_shift((explode(".",$_SERVER['HTTP_HOST'])));
    }
    $database_name = "phplist_mu_{$site}";</tt>
    """
    verbose_name = _("phpList SaaS")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'phplist'"
    serialize = True
    
    def error(self, msg):
        sys.stderr.write(msg + '\n')
        raise RuntimeError(msg)
    
    def _install_or_change_password(self, saas, server):
        """ configures the database for the new site through HTTP to /admin/ """
        admin_link = 'https://%s/admin/' % saas.get_site_domain()
        sys.stdout.write('admin_link: %s\n' % admin_link)
        admin_content = requests.get(admin_link, verify=settings.SAAS_PHPLIST_VERIFY_SSL)
        admin_content = admin_content.content.decode('utf8')
        if admin_content.startswith('Cannot connect to Database'):
            self.error("Database is not yet configured.")
        install = re.search(r'([^"]+firstinstall[^"]+)', admin_content)
        if install:
            if not hasattr(saas, 'password'):
                self.error("Password is missing.")
            install_path = install.groups()[0]
            install_link = admin_link + install_path[1:]
            post = {
                'adminname': saas.name,
                'orgname': saas.account.username,
                'adminemail': saas.account.username,
                'adminpassword': saas.password,
            }
            response = requests.post(
                install_link, data=post, verify=settings.SAAS_PHPLIST_VERIFY_SSL)
            sys.stdout.write(response.content.decode('utf8')+'\n')
            if response.status_code != 200:
                self.error("Bad status code %i." % response.status_code)
        else:
            md5_password = hashlib.md5()
            md5_password.update(saas.password.encode('ascii'))
            context = self.get_context(saas)
            context['digest'] = md5_password.hexdigest()
            cmd = textwrap.dedent("""\
                mysql \\
                    --host=%(db_host)s \\
                    --user=%(db_user)s \\
                    --password=%(db_pass)s \\
                    --execute='UPDATE phplist_admin SET password="%(digest)s" where ID=1; \\
                               UPDATE phplist_user_user SET password="%(digest)s" where ID=1;' \\
                    %(db_name)s""") % context
            sys.stdout.write('cmd: %s\n' % cmd)
            sshrun(server.get_address(), cmd, persist=True)
    
    def save(self, saas):
        if hasattr(saas, 'password'):
            self.append(self._install_or_change_password, saas)
        context = self.get_context(saas)
        if context['crontab']:
            context['escaped_crontab'] = context['crontab'].replace('$', '\\$')
            self.append(textwrap.dedent("""\
                # Configuring phpList crontabs
                if ! crontab -u %(user)s -l | grep 'phpList:"%(site_name)s"' > /dev/null; then
                cat << EOF | su - %(user)s --shell /bin/bash -c 'crontab'
                $(crontab -u %(user)s -l)
                
                # %(banner)s - phpList:"%(site_name)s"
                %(escaped_crontab)s
                EOF
                fi""") % context
            )
    
    def delete(self, saas):
        context = self.get_context(saas)
        if context['crontab']:
            context['crontab_regex'] = '\\|'.join(context['crontab'].splitlines())
            context['crontab_regex'] = context['crontab_regex'].replace('*', '\\*')
            self.append(textwrap.dedent("""\
                crontab -u %(user)s -l \\
                    | grep -v 'phpList:"%(site_name)s"\\|%(crontab_regex)s' \\
                    | su - %(user)s --shell /bin/bash -c 'crontab'
                """) % context
            )
    
    def get_context(self, saas):
        context = {
            'banner': self.get_banner(),
            'name': saas.name,
            'site_name': saas.name,
            'phplist_path': settings.SAAS_PHPLIST_PATH,
            'user': settings.SAAS_PHPLIST_SYSTEMUSER,
            'db_user': settings.SAAS_PHPLIST_DB_USER,
            'db_pass': settings.SAAS_PHPLIST_DB_PASS,
            'db_name': settings.SAAS_PHPLIST_DB_NAME,
            'db_host': settings.SAAS_PHPLIST_DB_HOST,
        }
        context.update({
            'crontab': settings.SAAS_PHPLIST_CRONTAB % context,
            'db_name': context['db_name'] % context,
        })
        return context


class PhpListTraffic(ServiceMonitor):
    verbose_name = _("phpList SaaS Traffic")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'phplist'"
    resource = ServiceMonitor.TRAFFIC
    script_executable = '/usr/bin/python'
    monthly_sum_old_values = True
    doc_settings = (settings,
        ('SAAS_PHPLIST_MAIL_LOG_PATH',)
    )
    
    def prepare(self):
        mail_log = settings.SAAS_PHPLIST_MAIL_LOG_PATH
        context = {
            'current_date': self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'mail_logs': str((mail_log, mail_log+'.1')),
        }
        self.append(textwrap.dedent("""\
            import sys
            from datetime import datetime
            from dateutil import tz
            
            def prepare(object_id, list_domain, ini_date):
                global lists
                ini_date = to_local_timezone(ini_date)
                ini_date = int(ini_date.strftime('%Y%m%d%H%M%S'))
                lists[list_domain] = [ini_date, object_id, 0]
            
            def inside_period(month, day, time, ini_date):
                global months
                global end_datetime
                # Mar  9 17:13:22
                month = months[month]
                year = end_datetime.year
                if month == '12' and end_datetime.month == 1:
                    year = year+1
                if len(day) == 1:
                    day = '0' + day
                date = str(year) + month + day
                date += time.replace(':', '')
                return ini_date < int(date) < end_date
            
            def to_local_timezone(date, tzlocal=tz.tzlocal()):
                # Converts orchestra's UTC dates to local timezone
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
                date = date.replace(tzinfo=tz.tzutc())
                date = date.astimezone(tzlocal)
                return date
            
            maillogs = {mail_logs}
            end_datetime = to_local_timezone('{current_date}')
            end_date = int(end_datetime.strftime('%Y%m%d%H%M%S'))
            months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
            months = dict((m, '%02d' % n) for n, m in enumerate(months, 1))
            
            lists = {{}}
            id_to_domain = {{}}
            
            def monitor(lists, id_to_domain, maillogs):
                for maillog in maillogs:
                    try:
                        with open(maillog, 'r') as maillog:
                            for line in maillog.readlines():
                                if ': message-id=<' in line:
                                    # Sep 15 09:36:51 web postfix/cleanup[8138]: C20FF244283: message-id=<fe94cc3afd20a9dc634cc9d9ed03fee0@u-romani.lists.pangea.org>
                                    month, day, time, __, __, id, message_id = line.split()[:7]
                                    list_domain = message_id.split('@')[1][:-1]
                                    try:
                                        opts = lists[list_domain]
                                    except KeyError:
                                        pass
                                    else:
                                        ini_date = opts[0]
                                        if inside_period(month, day, time, ini_date):
                                            id = id[:-1]
                                            id_to_domain[id] = list_domain
                                elif '>, size=' in line:
                                    # Sep 15 09:36:51 web postfix/qmgr[2296]: C20FF244283: from=<u-romani@pangea.org>, size=12252, nrcpt=1 (queue active)
                                    month, day, time, __, __, id, __, size = line.split()[:8]
                                    id = id[:-1]
                                    try:
                                        list_domain = id_to_domain[id]
                                    except KeyError:
                                        pass
                                    else:
                                        opts = lists[list_domain]
                                        size = int(size[5:-1])
                                        opts[2] += size
                    except IOError as e:
                        sys.stderr.write(str(e)+'\\n')
                for opts in lists.values():
                    print opts[1], opts[2]
            """).format(**context)
        )

    def commit(self):
        self.append('monitor(lists, id_to_domain, maillogs)')
    
    def monitor(self, saas):
        context = self.get_context(saas)
        self.append("prepare(%(object_id)s, '%(list_domain)s', '%(last_date)s')" % context)
    
    def get_context(self, saas):
        context = {
            'list_domain': saas.get_site_domain(),
            'object_id': saas.pk,
            'last_date': self.get_last_date(saas.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
        }
        return context
