import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from . import settings
from .models import List


class MailmanBackend(ServiceController):
    verbose_name = "Mailman"
    model = 'lists.List'
    addresses = [
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
    
    def include_virtual_alias_domain(self, context):
        # TODO  for list virtual_domains cleaning up we need to know the old domain name when a list changes its address
        #       domain, but this is not possible with the current design.
        #       sync the whole file everytime?
        # TODO same for mailbox virtual domains
        if context['address_domain']:
            self.append(textwrap.dedent("""
                [[ $(grep "^\s*%(address_domain)s\s*$" %(virtual_alias_domains)s) ]] || {
                    echo "%(address_domain)s" >> %(virtual_alias_domains)s
                    UPDATED_VIRTUAL_ALIAS_DOMAINS=1
                }""") % context
            )
    
    def exclude_virtual_alias_domain(self, context):
        address_domain = context['address_domain']
        if not List.objects.filter(address_domain=address_domain).exists():
            self.append('sed -i "/^%(address_domain)s\s*$/d" %(virtual_alias_domains)s' % context)
    
    def get_virtual_aliases(self, context):
        aliases = ['# %(banner)s' % context]
        for address in self.addresses:
            context['address'] = address
            aliases.append("%(address_name)s%(address)s@%(domain)s\t%(name)s%(address)s" % context)
        return '\n'.join(aliases)
    
    def save(self, mail_list):
        context = self.get_context(mail_list)
        # Create list
        self.append(textwrap.dedent("""\
            [[ ! -e %(mailman_root)s/lists/%(name)s ]] && {
                newlist --quiet --emailhost='%(domain)s' '%(name)s' '%(admin)s' '%(password)s'
            }""") % context)
        # Custom domain
        if mail_list.address:
            context['aliases'] = self.get_virtual_aliases(context)
            # Preserve indentation
            self.append(textwrap.dedent("""\
                if [[ ! $(grep '\s\s*%(name)s\s*$' %(virtual_alias)s) ]]; then
                    echo '%(aliases)s' >> %(virtual_alias)s
                    UPDATED_VIRTUAL_ALIAS=1
                else
                    if [[ ! $(grep '^\s*%(address_name)s@%(address_domain)s\s\s*%(name)s\s*$' %(virtual_alias)s) ]]; then
                        sed -i -e '/^.*\s%(name)s\(%(address_regex)s\)\s*$/d' \\
                               -e 'N; /^\s*\\n\s*$/d; P; D' %(virtual_alias)s
                        echo '%(aliases)s' >> %(virtual_alias)s
                        UPDATED_VIRTUAL_ALIAS=1
                    fi
                fi""") % context
            )
            self.append(
                'echo "require_explicit_destination = 0" | '
                '%(mailman_root)s/bin/config_list -i /dev/stdin %(name)s' % context
            )
            self.append(textwrap.dedent("""\
                echo "host_name = '%(address_domain)s'" | \
                    %(mailman_root)s/bin/config_list -i /dev/stdin %(name)s""") % context
            )
        else:
            # Cleanup shit
            self.append(textwrap.dedent("""\
                if [[ ! $(grep '\s\s*%(name)s\s*$' %(virtual_alias)s) ]]; then
                    sed -i "/^.*\s%(name)s\s*$/d" %(virtual_alias)s
                fi""") % context
            )
        # Update
        if context['password'] is not None:
            self.append(
                '%(mailman_root)s/bin/change_pw --listname="%(name)s" --password="%(password)s"' % context
            )
        self.include_virtual_alias_domain(context)
        if mail_list.active:
            self.append('chmod 775 %(mailman_root)s/lists/%(name)s' % context)
        else:
            self.append('chmod 000 %(mailman_root)s/lists/%(name)s' % context)
    
    def delete(self, mail_list):
        context = self.get_context(mail_list)
        self.exclude_virtual_alias_domain(context)
        self.append(textwrap.dedent("""
            sed -i -e '/^.*\s%(name)s\(%(address_regex)s\)\s*$/d' \\
                   -e 'N; /^\s*\\n\s*$/d; P; D' %(virtual_alias)s""") % context
        )
        self.append(textwrap.dedent("""
            # Non-existent list archives produce exit code 1
            exit_code=0
            rmlist -a %(name)s || exit_code=$?
            if [[ $exit_code != 0 && $exit_code != 1 ]]; then
                exit $exit_code
            fi""") % context
        )
    
    def commit(self):
        context = self.get_context_files()
        self.append(textwrap.dedent("""
            if [[ $UPDATED_VIRTUAL_ALIAS == 1 ]]; then
                postmap %(virtual_alias)s
            fi
            if [[ $UPDATED_VIRTUAL_ALIAS_DOMAINS == 1 ]]; then
                /etc/init.d/postfix reload
            fi""") % context
        )
    
    def get_context_files(self):
        return {
            'virtual_alias': settings.LISTS_VIRTUAL_ALIAS_PATH,
            'virtual_alias_domains': settings.LISTS_VIRTUAL_ALIAS_DOMAINS_PATH,
        }
    
    def get_banner(self, mail_list):
        banner = super(MailmanBackend, self).get_banner()
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
            'address_regex': '\|'.join(self.addresses),
            'admin': mail_list.admin_email,
            'mailman_root': settings.LISTS_MAILMAN_ROOT_PATH,
        })
        return context


class MailmanTrafficBash(ServiceMonitor):
    model = 'lists.List'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _("Mailman traffic (Bash)")
    
    def prepare(self):
        super(MailmanTraffic, self).prepare()
        context = {
            'mailman_log': '%s{,.1}' % settings.LISTS_MAILMAN_POST_LOG_PATH,
            'current_date': self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z"),
        }
        self.append(textwrap.dedent("""\
            function monitor () {
                OBJECT_ID=$1
                # Dates convertions are done server-side because of timezone discrepancies
                INI_DATE=$(date "+%%Y%%m%%d%%H%%M%%S" -d "$2")
                END_DATE=$(date '+%%Y%%m%%d%%H%%M%%S' -d '%(current_date)s')
                LIST_NAME="$3"
                MAILMAN_LOG=%(mailman_log)s
                
                SUBSCRIBERS=$(list_members ${LIST_NAME} | wc -l)
                {
                    { grep " post to ${LIST_NAME} " ${MAILMAN_LOG} || echo '\\r'; } \\
                        | awk -v ini="${INI_DATE}" -v end="${END_DATE}" -v subs="${SUBSCRIBERS}" '
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
                                # Mar 01 08:29:02 2015
                                month = months[$1]
                                day = $2
                                year = $4
                                split($3, time, ":")
                                line_date = year month day time[1] time[2] time[3]
                                if ( line_date > ini && line_date < end)
                                    sum += substr($11, 6, length($11)-6)
                            } END {
                                print sum * subs
                            }' || [[ $? == 1 ]] && true
                } | xargs echo ${OBJECT_ID}
            }""") % context)
    
    def monitor(self, mail_list):
        context = self.get_context(mail_list)
        self.append(
            'monitor %(object_id)i "%(last_date)s" "%(list_name)s"' % context
        )
    
    def get_context(self, mail_list):
        return {
            'list_name': mail_list.name,
            'object_id': mail_list.pk,
            'last_date': self.get_last_date(mail_list.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
        }


class MailmanTraffic(ServiceMonitor):
    model = 'lists.List'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _("Mailman traffic")
    script_executable = '/usr/bin/python'
    
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
                                month, day, time, year, __, __, __, list_name, __, __, size = line.split()[:11]
                                try:
                                    list = lists[list_name]
                                except KeyError:
                                    continue
                                else:
                                    date = year + months[month] + day + time.replace(':', '')
                                    if list[0] < int(date) < end_date:
                                        size = size[5:-1]
                                        try:
                                            list[2] += int(size)
                                        except ValueError:
                                            # anonymized post
                                            pass
                    except IOError as e:
                        sys.stderr.write(e)
                
                for list_name, opts in lists.items():
                    __, object_id, size = opts
                    if size:
                        cmd = ' '.join(('list_members', list_name, '| wc -l'))
                        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        subscribers = ps.communicate()[0].strip()
                        size *= int(subscribers)
                    print object_id, size
            """).format(**context)
        )
    
    def monitor(self, user):
        context = self.get_context(user)
        self.append("prepare(%(object_id)s, '%(list_name)s', '%(last_date)s')" % context)
    
    def commit(self):
        self.append('monitor(lists, end_date, months, postlogs)')
    
    def get_context(self, mail_list):
        return {
            'list_name': mail_list.name,
            'object_id': mail_list.pk,
            'last_date': self.get_last_date(mail_list.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
        }


class MailmanSubscribers(ServiceMonitor):
    model = 'lists.List'
    verbose_name = _("Mailman subscribers")
    
    def monitor(self, mail_list):
        context = self.get_context(mail_list)
        self.append('echo %(object_id)i $(list_members %(list_name)s | wc -l)' % context)
    
    def get_context(self, mail_list):
        return {
            'list_name': mail_list.name,
            'object_id': mail_list.pk,
        }
