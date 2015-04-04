import logging
import textwrap

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor
#from orchestra.utils.humanize import unit_to_bytes

from . import settings
from .models import Address

# TODO http://wiki2.dovecot.org/HowTo/SimpleVirtualInstall
# TODO http://wiki2.dovecot.org/HowTo/VirtualUserFlatFilesPostfix
# TODO mount the filesystem with "nosuid" option


logger = logging.getLogger(__name__)


class MailSystemUserBackend(ServiceController):
    verbose_name = _("Mail system users")
    model = 'mailboxes.Mailbox'
    
    def save(self, mailbox):
        context = self.get_context(mailbox)
        self.append(textwrap.dedent("""
            if [[ $( id %(user)s ) ]]; then
               usermod  %(user)s --password '%(password)s' --shell %(initial_shell)s
            else
               useradd %(user)s --home %(home)s --password '%(password)s'
            fi
            mkdir -p %(home)s
            chmod 751 %(home)s
            chown %(user)s:%(group)s %(home)s""") % context
        )
        if hasattr(mailbox, 'resources') and hasattr(mailbox.resources, 'disk'):
            self.set_quota(mailbox, context)
    
    def set_quota(self, mailbox, context):
        context['quota'] = mailbox.resources.disk.allocated * mailbox.resources.disk.resource.get_scale()
        #unit_to_bytes(mailbox.resources.disk.unit)
        self.append(textwrap.dedent("""
            mkdir -p %(home)s/Maildir
            chown %(user)s:%(group)s %(home)s/Maildir
            if [[ ! -f %(home)s/Maildir/maildirsize ]]; then
                echo "%(quota)iS" > %(home)s/Maildir/maildirsize
                chown %(user)s:%(group)s %(home)s/Maildir/maildirsize
            else
                sed -i '1s/.*/%(quota)iS/' %(home)s/Maildir/maildirsize
            fi""") % context
        )
    
    def delete(self, mailbox):
        context = self.get_context(mailbox)
        self.append('mv %(home)s %(home)s.deleted' % context)
        self.append(textwrap.dedent("""
            { sleep 2 && killall -u %(user)s -s KILL; } &
            killall -u %(user)s || true
            userdel %(user)s || true
            groupdel %(user)s || true""") % context
        )
    
    def get_context(self, mailbox):
        context = {
            'user': mailbox.name,
            'group': mailbox.name,
            'password': mailbox.password if mailbox.active else '*%s' % mailbox.password,
            'home': mailbox.get_home(),
            'initial_shell': '/dev/null',
        }
        return context


class PasswdVirtualUserBackend(ServiceController):
    verbose_name = _("Mail virtual user (passwd-file)")
    model = 'mailboxes.Mailbox'
    # TODO related_models = ('resources__content_type') ?? needed for updating disk usage from resource.data
    
    DEFAULT_GROUP = 'postfix'
    
    def set_user(self, context):
        self.append(textwrap.dedent("""
            if [[ $( grep "^%(user)s:" %(passwd_path)s ) ]]; then
               sed -i 's#^%(user)s:.*#%(passwd)s#' %(passwd_path)s
            else
               echo '%(passwd)s' >> %(passwd_path)s
            fi""") % context
        )
        self.append("mkdir -p %(home)s" % context)
        self.append("chown %(uid)s:%(gid)s %(home)s" % context)
    
    def set_mailbox(self, context):
        self.append(textwrap.dedent("""
            if [[ ! $(grep "^%(user)s@%(mailbox_domain)s\s" %(virtual_mailbox_maps)s) ]]; then
                echo "%(user)s@%(mailbox_domain)s\tOK" >> %(virtual_mailbox_maps)s
                UPDATED_VIRTUAL_MAILBOX_MAPS=1
            fi""") % context
        )
    
    def generate_filter(self, mailbox, context):
        self.append("doveadm mailbox create -u %(user)s Spam" % context)
        context['filtering_path'] = settings.MAILBOXES_SIEVE_PATH % context
        filtering = mailbox.get_filtering()
        if filtering:
            context['filtering'] = '# %(banner)s\n' + filtering
            self.append("mkdir -p $(dirname '%(filtering_path)s')" % context)
            self.append("echo '%(filtering)s' > %(filtering_path)s" % context)
        else:
            self.append("rm -f %(filtering_path)s" % context)
    
    def save(self, mailbox):
        context = self.get_context(mailbox)
        self.set_user(context)
        self.set_mailbox(context)
        self.generate_filter(mailbox, context)
    
    def delete(self, mailbox):
        context = self.get_context(mailbox)
        self.append("{ sleep 2 && killall -u %(uid)s -s KILL; } &" % context)
        self.append("killall -u %(uid)s || true" % context)
        self.append("sed -i '/^%(user)s:.*/d' %(passwd_path)s" % context)
        self.append("sed -i '/^%(user)s@%(mailbox_domain)s\s.*/d' %(virtual_mailbox_maps)s" % context)
        self.append("UPDATED_VIRTUAL_MAILBOX_MAPS=1")
        # TODO delete
        context['deleted'] = context['home'].rstrip('/') + '.deleted'
        self.append("mv %(home)s %(deleted)s" % context)
    
    def get_extra_fields(self, mailbox, context):
        context['quota'] = self.get_quota(mailbox)
        return 'userdb_mail=maildir:~/Maildir {quota}'.format(**context)
    
    def get_quota(self, mailbox):
        try:
            quota = mailbox.resources.disk.allocated
        except (AttributeError, ObjectDoesNotExist):
            return ''
        unit = mailbox.resources.disk.unit[0].upper()
        return 'userdb_quota_rule=*:bytes=%i%s' % (quota, unit)
    
    def commit(self):
        context = {
            'virtual_mailbox_maps': settings.MAILBOXES_VIRTUAL_MAILBOX_MAPS_PATH
        }
        self.append(textwrap.dedent("""\
            [[ $UPDATED_VIRTUAL_MAILBOX_MAPS == 1 ]] && {
                postmap %(virtual_mailbox_maps)s
            }""") % context
        )
    
    def get_context(self, mailbox):
        context = {
            'name': mailbox.name,
            'user': mailbox.name,
            'password': mailbox.password if mailbox.active else '*%s' % mailbox.password,
            'uid': 10000 + mailbox.pk,
            'gid': 10000 + mailbox.pk,
            'group': self.DEFAULT_GROUP,
            'quota': self.get_quota(mailbox),
            'passwd_path': settings.MAILBOXES_PASSWD_PATH,
            'home': mailbox.get_home().rstrip('/'),
            'banner': self.get_banner(),
            'virtual_mailbox_maps': settings.MAILBOXES_VIRTUAL_MAILBOX_MAPS_PATH,
            'mailbox_domain': settings.MAILBOXES_VIRTUAL_MAILBOX_DEFAULT_DOMAIN,
        }
        context['extra_fields'] = self.get_extra_fields(mailbox, context)
        context['passwd'] = '{user}:{password}:{uid}:{gid}::{home}::{extra_fields}'.format(**context)
        return context


class PostfixAddressBackend(ServiceController):
    verbose_name = _("Postfix address")
    model = 'mailboxes.Address'
    related_models = (
        ('mailboxes.Mailbox', 'addresses'),
    )
    
    def include_virtual_alias_domain(self, context):
        self.append(textwrap.dedent("""
            [[ $(grep "^\s*%(domain)s\s*$" %(virtual_alias_domains)s) ]] || {
                echo "%(domain)s" >> %(virtual_alias_domains)s
                UPDATED_VIRTUAL_ALIAS_DOMAINS=1
            }""") % context)
    
    def exclude_virtual_alias_domain(self, context):
        domain = context['domain']
        if not Address.objects.filter(domain=domain).exists():
            self.append('sed -i "/^%(domain)s\s*/d" %(virtual_alias_domains)s' % context)
    
    def update_virtual_alias_maps(self, address, context):
        # Virtual mailbox stuff
#        destination = []
#        for mailbox in address.get_mailboxes():
#            context['mailbox'] = mailbox
#            destination.append("%(mailbox)s@%(mailbox_domain)s" % context)
#        for forward in address.forward:
#            if '@' in forward:
#                destination.append(forward)
        destination = address.destination
        if destination:
            context['destination'] = destination
            self.append(textwrap.dedent("""
                LINE="%(email)s\t%(destination)s"
                if [[ ! $(grep "^%(email)s\s" %(virtual_alias_maps)s) ]]; then
                   echo "${LINE}" >> %(virtual_alias_maps)s
                   UPDATED_VIRTUAL_ALIAS_MAPS=1
                else
                   if [[ ! $(grep "^${LINE}$" %(virtual_alias_maps)s) ]]; then
                       sed -i "s/^%(email)s\s.*$/${LINE}/" %(virtual_alias_maps)s
                       UPDATED_VIRTUAL_ALIAS_MAPS=1
                   fi
                fi""") % context)
        else:
            logger.warning("Address %i is empty" % address.pk)
            self.append('sed -i "/^%(email)s\s/d" %(virtual_alias_maps)s' % context)
            self.append('UPDATED_VIRTUAL_ALIAS_MAPS=1')
    
    def exclude_virtual_alias_maps(self, context):
        self.append(textwrap.dedent("""
            if [[ $(grep "^%(email)s\s" %(virtual_alias_maps)s) ]]; then
               sed -i "/^%(email)s\s.*$/d" %(virtual_alias_maps)s
               UPDATED_VIRTUAL_ALIAS_MAPS=1
            fi""") % context)
    
    def save(self, address):
        context = self.get_context(address)
        self.include_virtual_alias_domain(context)
        self.update_virtual_alias_maps(address, context)
    
    def delete(self, address):
        context = self.get_context(address)
        self.exclude_virtual_alias_domain(context)
        self.exclude_virtual_alias_maps(context)
    
    def commit(self):
        context = self.get_context_files()
        self.append(textwrap.dedent("""
            [[ $UPDATED_VIRTUAL_ALIAS_MAPS == 1 ]] && { postmap %(virtual_alias_maps)s; }
            [[ $UPDATED_VIRTUAL_ALIAS_DOMAINS == 1 ]] && { /etc/init.d/postfix reload; }
            """) % context
        )
        self.append('exit 0')
    
    def get_context_files(self):
        return {
            'virtual_alias_domains': settings.MAILBOXES_VIRTUAL_ALIAS_DOMAINS_PATH,
            'virtual_alias_maps': settings.MAILBOXES_VIRTUAL_ALIAS_MAPS_PATH
        }
    
    def get_context(self, address):
        context = self.get_context_files()
        context.update({
            'domain': address.domain,
            'email': address.email,
            'mailbox_domain': settings.MAILBOXES_VIRTUAL_MAILBOX_DEFAULT_DOMAIN,
        })
        return context


class AutoresponseBackend(ServiceController):
    verbose_name = _("Mail autoresponse")
    model = 'mail.Autoresponse'


class MaildirDisk(ServiceMonitor):
    """
    Maildir disk usage based on Dovecot maildirsize file
    
    http://wiki2.dovecot.org/Quota/Maildir
    """
    model = 'mailboxes.Mailbox'
    resource = ServiceMonitor.DISK
    verbose_name = _("Maildir disk usage")
    
    def prepare(self):
        super(MaildirDisk, self).prepare()
        current_date = self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z")
        self.append(textwrap.dedent("""\
            function monitor () {
                awk 'BEGIN { size = 0 } NR > 1 { size += $1 } END { print size }' $1 || echo 0
            }"""))
    
    def monitor(self, mailbox):
        context = self.get_context(mailbox)
        self.append("echo %(object_id)s $(monitor %(maildir_path)s)" % context)
    
    def get_context(self, mailbox):
        context = {
            'home': mailbox.get_home(),
            'object_id': mailbox.pk
        }
        context['maildir_path'] = settings.MAILBOXES_MAILDIRSIZE_PATH % context
        return context


class PostfixTraffic(ServiceMonitor):
    """
    A high-performance log parser
    Reads the mail.log file only once, for all users
    """
    model = 'mailboxes.Mailbox'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _("Postfix traffic usage")
    script_executable = '/usr/bin/python'
    
    def prepare(self):
        mail_log = '/var/log/mail.log'
        context = {
            'current_date': self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'mail_logs': str((mail_log, mail_log+'.1')),
        }
        self.append(textwrap.dedent("""\
            import re
            import sys
            from datetime import datetime
            from dateutil import tz
            
            def to_local_timezone(date, tzlocal=tz.tzlocal()):
                # Converts orchestra's UTC dates to local timezone
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
                date = date.replace(tzinfo=tz.tzutc())
                date = date.astimezone(tzlocal)
                return date
            
            maillogs = {mail_logs}
            end_datetime = to_local_timezone('{current_date}')
            end_date = int(end_datetime.strftime('%Y%m%d%H%M%S'))
            months = {{
                "Jan": "01",
                "Feb": "02",
                "Mar": "03",
                "Apr": "04",
                "May": "05",
                "Jun": "06",
                "Jul": "07",
                "Aug": "08",
                "Sep": "09",
                "Oct": "10",
                "Nov": "11",
                "Dec": "12",
            }}
            
            def inside_period(month, day, time, ini_date):
                global months
                global end_datetime
                # Mar 19 17:13:22
                month = months[month]
                year = end_datetime.year
                if month == '12' and end_datetime.month == 1:
                    year = year+1
                date = str(year) + month + day
                date += time.replace(':', '')
                return ini_date < int(date) < end_date
            
            users = {{}}
            delivers = {{}}
            reverse = {{}}
            
            def prepare(object_id, mailbox, ini_date):
                global users
                global delivers
                global reverse
                ini_date = to_local_timezone(ini_date)
                ini_date = int(ini_date.strftime('%Y%m%d%H%M%S'))
                users[mailbox] = (ini_date, object_id)
                delivers[mailbox] = set()
                reverse[mailbox] = set()
            
            def monitor(users, delivers, reverse, maillogs):
                targets = {{}}
                counter = {{}}
                user_regex = re.compile(r'\(Authenticated sender: ([^ ]+)\)')
                for maillog in maillogs:
                    try:
                        with open(maillog, 'r') as maillog:
                            for line in maillog.readlines():
                                # Only search for Authenticated sendings
                                if '(Authenticated sender: ' in line:
                                    username = user_regex.search(line).groups()[0]
                                    try:
                                        sender = users[username]
                                    except KeyError:
                                        continue
                                    else:
                                        month, day, time, __, proc, id = line.split()[:6]
                                        if inside_period(month, day, time, sender[0]):
                                            # Add new email
                                            delivers[id[:-1]] = username
                                # Look for a MailScanner requeue ID
                                elif ' Requeue: ' in line:
                                    id, __, req_id = line.split()[6:9]
                                    id = id.split('.')[0]
                                    try:
                                        username = delivers[id]
                                    except KeyError:
                                        pass
                                    else:
                                        targets[req_id] = (username, None)
                                        reverse[username].add(req_id)
                                # Look for the mail size and count the number of recipients of each email
                                else:
                                    try:
                                        month, day, time, __, proc, req_id, __, msize = line.split()[:8]
                                    except ValueError:
                                        # not interested in this line
                                        continue
                                    if proc.startswith('postfix/'):
                                        req_id = req_id[:-1]
                                        if msize.startswith('size='):
                                            try:
                                                target = targets[req_id]
                                            except KeyError:
                                                pass
                                            else:
                                                targets[req_id] = (target[0], int(msize[5:-1]))
                                        elif proc.startswith('postfix/smtp'):
                                            try:
                                                target = targets[req_id]
                                            except KeyError:
                                                pass
                                            else:
                                                if inside_period(month, day, time, users[target[0]][0]):
                                                    try:
                                                        counter[req_id] += 1
                                                    except KeyError:
                                                        counter[req_id] = 1
                    except IOError as e:
                        sys.stderr.write(e)
                    
                for username, opts in users.items():
                    size = 0
                    for req_id in reverse[username]:
                        size += targets[req_id][1] * counter.get(req_id, 0)
                    print opts[1], size
            """).format(**context)
        )
    
    def commit(self):
        self.append('monitor(users, delivers, reverse, maillogs)')
    
    def monitor(self, mailbox):
        context = self.get_context(mailbox)
        self.append("prepare(%(object_id)s, '%(mailbox)s', '%(last_date)s')" % context)
    
    def get_context(self, mailbox):
        return {
#            'mainlog': settings.LISTS_MAILMAN_POST_LOG_PATH,
            'mailbox': mailbox.name,
            'object_id': mailbox.pk,
            'last_date': self.get_last_date(mailbox.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
        }





