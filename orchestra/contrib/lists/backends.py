import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace
from orchestra.contrib.resources import ServiceMonitor

from . import settings
from .models import List


class MailmanVirtualDomainController(ServiceController):
    """
    Only syncs virtualdomains used on mailman addresses
    """
    verbose_name = _("Mailman virtdomain-only")
    model = 'lists.List'
    doc_settings = (settings,
        ('LISTS_VIRTUAL_ALIAS_DOMAINS_PATH',)
    )
    
    def is_hosted_domain(self, domain):
        """ whether or not domain MX points to this server """
        return domain.has_default_mx()
    
    def include_virtual_alias_domain(self, context):
        domain = context['address_domain']
        if domain and self.is_hosted_domain(domain):
            self.append(textwrap.dedent("""
                # Add virtual domain %(address_domain)s
                [[ $(grep '^\s*%(address_domain)s\s*$' %(virtual_alias_domains)s) ]] || {
                    echo '%(address_domain)s' >> %(virtual_alias_domains)s
                    UPDATED_VIRTUAL_ALIAS_DOMAINS=1
                }""") % context
            )
    
    def is_last_domain(self, domain):
        return not List.objects.filter(address_domain=domain).exists()
    
    def exclude_virtual_alias_domain(self, context):
        domain = context['address_domain']
        if domain and self.is_last_domain(domain):
            self.append(textwrap.dedent("""
                # Remove %(address_domain)s from virtual domains
                sed -i '/^%(address_domain)s\s*$/d' %(virtual_alias_domains)s\
                """) % context
            )
    
    def save(self, mail_list):
        context = self.get_context(mail_list)
        #self.include_virtual_alias_domain(context)
    
    def delete(self, mail_list):
        context = self.get_context(mail_list)
        #self.exclude_virtual_alias_domain(context)
    
    def commit(self):
        context = self.get_context_files()
        super(MailmanVirtualDomainController, self).commit()
    
    def get_context_files(self):
        return {
            'virtual_alias_domains': settings.LISTS_VIRTUAL_ALIAS_DOMAINS_PATH,
        }
    
    def get_context(self, mail_list):
        context = self.get_context_files()
        context.update({
            'address_domain': mail_list.address_domain,
        })
        return replace(context, "'", '"')


class MailmanController(MailmanVirtualDomainController):
    """
    Mailman 2 backend based on <tt>newlist</tt>, it handles custom domains.
    Includes <tt>MailmanVirtualDomainController</tt>
    """
    verbose_name = "Mailman"
    address_suffixes = [
        '',
        '-admin',
        '-bounces',
        '-confirm',
        '-join',
        '-leave',
        '-owner',
        '-request',
        '-subscribe',
        '-unsubscribe'
    ]
    doc_settings = (settings, (
        'LISTS_VIRTUAL_ALIAS_PATH',
        'LISTS_VIRTUAL_ALIAS_DOMAINS_PATH',
        'LISTS_DEFAULT_DOMAIN',
        'LISTS_MAILMAN_ROOT_DIR'
    ))
    
    def get_virtual_aliases(self, context):
        aliases = ['# %(banner)s' % context]
        for suffix in self.address_suffixes:
            context['suffix'] = suffix
            # Because mailman doesn't properly handle lists aliases we need two virtual aliases
            aliases.append("%(address_name)s%(suffix)s@%(domain)s\t%(name)s%(suffix)s@grups.pangea.org" % context)
            if context['address_name'] != context['name']:
                # And another with the original list name; Mailman generates links with it
                aliases.append("%(name)s%(suffix)s@%(domain)s\t%(name)s%(suffix)s" % context)
        return '\n'.join(aliases)
    
    def save(self, mail_list):
        context = self.get_context(mail_list)
        # Create list
        cmd = "/opt/mailman/venv/bin/python /usr/local/admin/orchestra_mailman3/save.py %(name)s %(admin)s %(address_name)s@%(domain)s" % context
        if not mail_list.active:
            cmd += ' --inactive'
        self.append(cmd)

    def delete(self, mail_list):
        context = self.get_context(mail_list)
        # Delete list
        cmd = "/opt/mailman/venv/bin/python /usr/local/admin/orchestra_mailman3/delete.py %(name)s %(admin)s %(address_name)s@%(domain)s" % context
        if not mail_list.active:
            cmd += ' --inactive'
        self.append(cmd)
    
    def commit(self):
        pass

    def get_context_files(self):
        return {
            'virtual_alias': settings.LISTS_VIRTUAL_ALIAS_PATH,
            'virtual_alias_domains': settings.LISTS_VIRTUAL_ALIAS_DOMAINS_PATH,
        }
    
    def get_banner(self, mail_list):
        banner = super(MailmanController, self).get_banner()
        return '%s %s' % (banner, mail_list.name)
    
    def get_context(self, mail_list):
        context = self.get_context_files()
        context.update({
            'banner': self.get_banner(mail_list),
            'name': mail_list.name,
            'password': mail_list.password,
            'domain': mail_list.address_domain or settings.LISTS_DEFAULT_DOMAIN,
            'address_name': mail_list.get_address_name(),
            'address_domain': mail_list.address_domain,
            'suffixes_regex': '\|'.join(self.address_suffixes),
            'admin': mail_list.admin_email,
            'mailman_root': settings.LISTS_MAILMAN_ROOT_DIR,
        })
        return replace(context, "'", '"')


class MailmanTraffic(ServiceMonitor):
    """
    Parses mailman log file looking for email size and multiples it by <tt>list_members</tt> count.
    """
    model = 'lists.List'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _("Mailman traffic")
    script_executable = '/usr/bin/python'
    monthly_sum_old_values = True
    doc_settings = (settings,
        ('LISTS_MAILMAN_POST_LOG_PATH',)
    )
    
    def prepare(self):
        postlog = settings.LISTS_MAILMAN_POST_LOG_PATH
        context = {
            'postlogs': str((postlog, postlog+'.1')),
            'current_date': self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z"),
        }
        self.append(textwrap.dedent("""\
            import re
            import subprocess
            import sys
            from datetime import datetime
            from dateutil import tz
            
            def to_local_timezone(date, tzlocal=tz.tzlocal()):
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
                date = date.replace(tzinfo=tz.tzutc())
                date = date.astimezone(tzlocal)
                return date
            
            postlogs = {postlogs}
            # Use local timezone
            end_date = to_local_timezone('{current_date}')
            end_date = int(end_date.strftime('%Y%m%d%H%M%S'))
            lists = {{}}
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
            mailman_addr = re.compile(r'.*-(admin|bounces|confirm|join|leave|owner|request|subscribe|unsubscribe)@.*|mailman@.*')
            
            def prepare(object_id, list_name, ini_date):
                global lists
                ini_date = to_local_timezone(ini_date)
                ini_date = int(ini_date.strftime('%Y%m%d%H%M%S'))
                lists[list_name] = [ini_date, object_id, 0]
            
            def monitor(lists, end_date, months, postlogs):
                for postlog in postlogs:
                    try:
                        with open(postlog, 'r') as postlog:
                            for line in postlog.readlines():
                                line = line.split()
                                if len(line) < 11:
                                    continue
                                month, day, time, year, __, __, __, list_name, __, addr, size = line[:11]
                                try:
                                    list = lists[list_name]
                                except KeyError:
                                    continue
                                else:
                                    # discard mailman messages because of inconsistent POST logging
                                    if mailman_addr.match(addr):
                                        continue
                                    date = year + months[month] + day + time.replace(':', '')
                                    if list[0] < int(date) < end_date:
                                        size = size[5:-1]
                                        try:
                                            list[2] += int(size)
                                        except ValueError:
                                            # anonymized post
                                            pass
                    except IOError as e:
                        sys.stderr.write(str(e)+'\\n')
                
                for list_name, opts in lists.items():
                    __, object_id, size = opts
                    if size:
                        cmd = ' '.join(('list_members', list_name, '| wc -l'))
                        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        subscribers = ps.communicate()[0].strip()
                        size *= int(subscribers)
                        sys.stderr.write("%s %s*%s traffic*subscribers\\n" % (object_id, size, subscribers))
                    print object_id, size
            """).format(**context)
        )
    
    def monitor(self, user):
        context = self.get_context(user)
        self.append("prepare(%(object_id)s, '%(list_name)s', '%(last_date)s')" % context)
    
    def commit(self):
        self.append('monitor(lists, end_date, months, postlogs)')
    
    def get_context(self, mail_list):
        context = {
            'list_name': mail_list.name,
            'object_id': mail_list.pk,
            'last_date': self.get_last_date(mail_list.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
        }
        return replace(context, "'", '"')


class MailmanSubscribers(ServiceMonitor):
    """
    Monitors number of list subscribers via <tt>list_members</tt>
    """
    model = 'lists.List'
    verbose_name = _("Mailman subscribers")
    delete_old_equal_values = True
    
    def monitor(self, mail_list):
        context = self.get_context(mail_list)
        self.append('echo %(object_id)i $(list_members %(list_name)s | wc -l)' % context)
    
    def get_context(self, mail_list):
        context = {
            'list_name': mail_list.name,
            'object_id': mail_list.pk,
        }
        return replace(context, "'", '"')
