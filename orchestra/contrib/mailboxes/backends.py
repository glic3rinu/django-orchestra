import logging
import os
import re
import textwrap

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController
from orchestra.contrib.resources import ServiceMonitor

from . import settings
from .models import Address, Mailbox


logger = logging.getLogger(__name__)


class SieveFilteringMixin:
    def generate_filter(self, mailbox, context):
        name, content = mailbox.get_filtering()
        for box in re.findall(r'fileinto\s+"([^"]+)"', content):
            # create mailboxes if fileinfo is provided witout ':create' option
            context['box'] = box
            self.append(textwrap.dedent("""
                # Create %(box)s mailbox
                su - %(user)s --shell /bin/bash << 'EOF'
                    mkdir -p "%(maildir)s/.%(box)s"
                EOF
                if ! grep '%(box)s' %(maildir)s/subscriptions > /dev/null; then
                    echo '%(box)s' >> %(maildir)s/subscriptions
                    chown %(user)s:%(user)s %(maildir)s/subscriptions
                fi
                """) % context
            )
        context['filtering_path'] = settings.MAILBOXES_SIEVE_PATH % context
        context['filtering_cpath'] = re.sub(r'\.sieve$', '.svbin', context['filtering_path'])
        if content:
            context['filtering'] = ('# %(banner)s\n' + content) % context
            self.append(textwrap.dedent("""\
                # Create and compile orchestra sieve filtering
                su - %(user)s --shell /bin/bash << 'EOF'
                    mkdir -p $(dirname "%(filtering_path)s")
                    cat << '    EOF' > %(filtering_path)s
                %(filtering)s
                    EOF
                    sievec %(filtering_path)s
                EOF
                """) % context
            )
        else:
            self.append("echo '' > %(filtering_path)s" % context)
        self.append('chown %(user)s:%(group)s %(filtering_path)s' % context)


class UNIXUserMaildirController(SieveFilteringMixin, ServiceController):
    """
    Assumes that all system users on this servers all mail accounts.
    If you want to have system users AND mailboxes on the same server you should consider using virtual mailboxes.
    Supports quota allocation via <tt>resources.disk.allocated</tt>.
    """
    SHELL = '/dev/null'
    
    verbose_name = _("UNIX maildir user")
    model = 'mailboxes.Mailbox'
    
    def save(self, mailbox):
        context = self.get_context(mailbox)
        self.append(textwrap.dedent("""
            # Update/create %(user)s user state
            if id %(user)s ; then
                old_password=$(getent shadow %(user)s | cut -d':' -f2)
                usermod %(user)s \\
                    --shell %(initial_shell)s \\
                    --password '%(password)s'
                if [[ "$old_password" != '%(password)s' ]]; then
                    # Postfix SASL caches passwords
                    RESTART_POSTFIX=1
                fi
            else
                useradd %(user)s \\
                    --home %(home)s \\
                    --password '%(password)s'
            fi
            mkdir -p %(home)s
            chmod 751 %(home)s
            chown %(user)s:%(group)s %(home)s""") % context
        )
        if hasattr(mailbox, 'resources') and hasattr(mailbox.resources, 'disk'):
            self.set_quota(mailbox, context)
        self.generate_filter(mailbox, context)
    
    def set_quota(self, mailbox, context):
        allocated = mailbox.resources.disk.allocated
        scale = mailbox.resources.disk.resource.get_scale()
        context['quota'] = allocated * scale
        #unit_to_bytes(mailbox.resources.disk.unit)
        self.append(textwrap.dedent("""
            # Set Maildir quota for %(user)s
            su - %(user)s --shell /bin/bash << 'EOF'
                mkdir -p %(maildir)s
            EOF
            if [ ! -f %(maildir)s/maildirsize ]; then
                echo "%(quota)iS" > %(maildir)s/maildirsize
                chown %(user)s:%(group)s %(maildir)s/maildirsize
            else
                sed -i '1s/.*/%(quota)iS/' %(maildir)s/maildirsize
            fi""") % context
        )
    
    def delete(self, mailbox):
        context = self.get_context(mailbox)
        if context['deleted_home']:
            self.append(textwrap.dedent("""\
                # Move home into MAILBOXES_MOVE_ON_DELETE_PATH, nesting if exists.
                deleted_home="%(deleted_home)s"
                while [[ -e $deleted_home ]]; do
                    deleted_home="${deleted_home}/$(basename ${deleted_home})"
                done
                mv %(home)s $deleted_home || exit_code=$?
                """) % context
            )
        else:
            self.append("rm -fr -- %(base_home)s" % context)
        self.append(textwrap.dedent("""
            nohup bash -c '{ sleep 2 && killall -u %(user)s -s KILL; }' &> /dev/null &
            killall -u %(user)s || true
            # Restart because of Postfix SASL caching credentials
            userdel %(user)s && RESTART_POSTFIX=1 || true
            groupdel %(user)s || true""") % context
        )
    
    def commit(self):
        self.append('[[ $RESTART_POSTFIX -eq 1 ]] && service postfix restart')
        super().commit()
    
    def get_context(self, mailbox):
        context = {
            'user': mailbox.name,
            'group': mailbox.name,
            'name': mailbox.name,
            'password': mailbox.password if mailbox.active else '*%s' % mailbox.password,
            'home': mailbox.get_home(),
            'maildir': os.path.join(mailbox.get_home(), 'Maildir'),
            'initial_shell': self.SHELL,
            'banner': self.get_banner(),
        }
        context['deleted_home'] = settings.MAILBOXES_MOVE_ON_DELETE_PATH % context
        return context


#class DovecotPostfixPasswdVirtualUserController(SieveFilteringMixin, ServiceController):
#    """
#    WARNING: This backends is not fully implemented
#    """
#    DEFAULT_GROUP = 'postfix'
#    
#    verbose_name = _("Dovecot-Postfix virtualuser")
#    model = 'mailboxes.Mailbox'
#    
#    def set_user(self, context):
#        self.append(textwrap.dedent("""
#            if grep '^%(user)s:' %(passwd_path)s > /dev/null ; then
#               sed -i 's#^%(user)s:.*#%(passwd)s#' %(passwd_path)s
#            else
#               echo '%(passwd)s' >> %(passwd_path)s
#            fi""") % context
#        )
#        self.append("mkdir -p %(home)s" % context)
#        self.append("chown %(uid)s:%(gid)s %(home)s" % context)
#    
#    def set_mailbox(self, context):
#        self.append(textwrap.dedent("""
#            if ! grep '^%(user)s@%(mailbox_domain)s\s' %(virtual_mailbox_maps)s > /dev/null; then
#                echo "%(user)s@%(mailbox_domain)s\tOK" >> %(virtual_mailbox_maps)s
#                UPDATED_VIRTUAL_MAILBOX_MAPS=1
#            fi""") % context
#        )
#    
#    def save(self, mailbox):
#        context = self.get_context(mailbox)
#        self.set_user(context)
#        self.set_mailbox(context)
#        self.generate_filter(mailbox, context)
#    
#    def delete(self, mailbox):
#        context = self.get_context(mailbox)
#        self.append(textwrap.dedent("""
#            nohup bash -c 'sleep 2 && killall -u %(uid)s -s KILL' &> /dev/null &
#            killall -u %(uid)s || true
#            sed -i '/^%(user)s:.*/d' %(passwd_path)s
#            sed -i '/^%(user)s@%(mailbox_domain)s\s.*/d' %(virtual_mailbox_maps)s
#            UPDATED_VIRTUAL_MAILBOX_MAPS=1""") % context
#        )
#        if context['deleted_home']:
#            self.append("mv %(home)s %(deleted_home)s || exit_code=$?" % context)
#        else:
#            self.append("rm -fr -- %(home)s" % context)
#    
#    def get_extra_fields(self, mailbox, context):
#        context['quota'] = self.get_quota(mailbox)
#        return 'userdb_mail=maildir:~/Maildir {quota}'.format(**context)
#    
#    def get_quota(self, mailbox):
#        try:
#            quota = mailbox.resources.disk.allocated
#        except (AttributeError, ObjectDoesNotExist):
#            return ''
#        unit = mailbox.resources.disk.unit[0].upper()
#        return 'userdb_quota_rule=*:bytes=%i%s' % (quota, unit)
#    
#    def commit(self):
#        context = {
#            'virtual_mailbox_maps': settings.MAILBOXES_VIRTUAL_MAILBOX_MAPS_PATH
#        }
#        self.append(textwrap.dedent("""
#            [[ $UPDATED_VIRTUAL_MAILBOX_MAPS == 1 ]] && {
#                postmap %(virtual_mailbox_maps)s
#            }""") % context
#        )
#    
#    def get_context(self, mailbox):
#        context = {
#            'name': mailbox.name,
#            'user': mailbox.name,
#            'password': mailbox.password if mailbox.active else '*%s' % mailbox.password,
#            'uid': 10000 + mailbox.pk,
#            'gid': 10000 + mailbox.pk,
#            'group': self.DEFAULT_GROUP,
#            'quota': self.get_quota(mailbox),
#            'passwd_path': settings.MAILBOXES_PASSWD_PATH,
#            'home': mailbox.get_home(),
#            'banner': self.get_banner(),
#            'virtual_mailbox_maps': settings.MAILBOXES_VIRTUAL_MAILBOX_MAPS_PATH,
#            'mailbox_domain': settings.MAILBOXES_VIRTUAL_MAILBOX_DEFAULT_DOMAIN,
#        }
#        context['extra_fields'] = self.get_extra_fields(mailbox, context)
#        context.update({
#            'passwd': '{user}:{password}:{uid}:{gid}::{home}::{extra_fields}'.format(**context),
#            'deleted_home': settings.MAILBOXES_MOVE_ON_DELETE_PATH % context,
#        })
#        return context


class PostfixAddressVirtualDomainController(ServiceController):
    """
    Secondary SMTP server without mailboxes in it, only syncs virtual domains.
    """
    verbose_name = _("Postfix address virtdomain-only")
    model = 'mailboxes.Address'
    related_models = (
        ('mailboxes.Mailbox', 'addresses'),
    )
    doc_settings = (settings,
        ('MAILBOXES_LOCAL_DOMAIN', 'MAILBOXES_VIRTUAL_ALIAS_DOMAINS_PATH')
    )
    
    def is_hosted_domain(self, domain):
        """ whether or not domain MX points to this server """
        return domain.has_default_mx()
    
    def include_virtual_alias_domain(self, context):
        domain = context['domain']
        if domain.name != context['local_domain'] and self.is_hosted_domain(domain):
            self.append(textwrap.dedent("""
                # %(domain)s is a virtual domain belonging to this server
                if ! grep '^\s*%(domain)s\s*$' %(virtual_alias_domains)s > /dev/null; then
                    echo '%(domain)s' >> %(virtual_alias_domains)s
                    UPDATED_VIRTUAL_ALIAS_DOMAINS=1
                fi""") % context
            )
    
    def is_last_domain(self, domain):
        return not Address.objects.filter(domain=domain).exists()
    
    def exclude_virtual_alias_domain(self, context):
        domain = context['domain']
        if self.is_last_domain(domain):
            # Prevent deleting the same domain multiple times on bulk deletes
            if not hasattr(self, '_excluded_domains'):
                self._excluded_domains = set()
            if domain.name not in self._excluded_domains:
                self._excluded_domains.add(domain.name)
                self.append(textwrap.dedent("""
                    # Delete %(domain)s virtual domain
                    if grep '^%(domain)s\s*$' %(virtual_alias_domains)s > /dev/null; then
                        sed -i '/^%(domain)s\s*/d' %(virtual_alias_domains)s
                        UPDATED_VIRTUAL_ALIAS_DOMAINS=1
                    fi""") % context
                )
    
    def save(self, address):
        context = self.get_context(address)
        self.include_virtual_alias_domain(context)
        return context
    
    def delete(self, address):
        context = self.get_context(address)
        self.exclude_virtual_alias_domain(context)
        return context
    
    def commit(self):
        context = self.get_context_files()
        self.append(textwrap.dedent("""
            [[ $UPDATED_VIRTUAL_ALIAS_DOMAINS == 1 ]] && {
                service postfix reload
            }
            exit $exit_code
            """) % context
        )
    
    def get_context_files(self):
        return {
            'virtual_alias_domains': settings.MAILBOXES_VIRTUAL_ALIAS_DOMAINS_PATH,
            'virtual_alias_maps': settings.MAILBOXES_VIRTUAL_ALIAS_MAPS_PATH
        }
    
    def get_context(self, address):
        context = self.get_context_files()
        context.update({
            'name': address.name,
            'domain': address.domain,
            'email': address.email,
            'local_domain': settings.MAILBOXES_LOCAL_DOMAIN,
        })
        return context


class PostfixAddressController(PostfixAddressVirtualDomainController):
    """
    Addresses based on Postfix virtual alias domains, includes <tt>PostfixAddressVirtualDomainController</tt>.
    """
    verbose_name = _("Postfix address")
    doc_settings = (settings, (
        'MAILBOXES_LOCAL_DOMAIN',
        'MAILBOXES_VIRTUAL_ALIAS_DOMAINS_PATH',
        'MAILBOXES_VIRTUAL_ALIAS_MAPS_PATH'
    ))
    
    def is_implicit_entry(self, context):
        """
        check if virtual_alias_map entry can be omitted because the address is
        equivalent to its local mbox
        """
        return bool(
            context['domain'].name == context['local_domain'] and
            context['destination'] == context['name'] and
            Mailbox.objects.filter(name=context['name']).exists())
    
    def update_virtual_alias_maps(self, address, context):
        context['destination'] = address.destination
        if not self.is_implicit_entry(context):
            self.append(textwrap.dedent("""
                # Set virtual alias entry for %(email)s
                LINE='%(email)s\t%(destination)s'
                if ! grep '^%(email)s\s' %(virtual_alias_maps)s > /dev/null; then
                    # Add new line
                    echo "${LINE}" >> %(virtual_alias_maps)s
                    UPDATED_VIRTUAL_ALIAS_MAPS=1
                else
                    # Update existing line, if needed
                    if ! grep "^${LINE}$" %(virtual_alias_maps)s > /dev/null; then
                        sed -i "s/^%(email)s\s.*$/${LINE}/" %(virtual_alias_maps)s
                        UPDATED_VIRTUAL_ALIAS_MAPS=1
                    fi
                fi""") % context)
        else:
            if not context['destination']:
                msg = "Address %i is empty" % address.pk
                self.append("\necho 'msg' >&2" % msg)
                logger.warning(msg)
            else:
                self.append("\n# %(email)s %(destination)s entry is redundant" % context)
            self.exclude_virtual_alias_maps(context)
        # Virtual mailbox stuff
#        destination = []
#        for mailbox in address.get_mailboxes():
#            context['mailbox'] = mailbox
#            destination.append("%(mailbox)s@%(local_domain)s" % context)
#        for forward in address.forward:
#            if '@' in forward:
#                destination.append(forward)
    
    def exclude_virtual_alias_maps(self, context):
        self.append(textwrap.dedent("""\
            # Remove %(email)s virtual alias entry
            if grep '^%(email)s\s' %(virtual_alias_maps)s > /dev/null; then
                sed -i '/^%(email)s\s/d' %(virtual_alias_maps)s
                UPDATED_VIRTUAL_ALIAS_MAPS=1
            fi""") % context
        )
    
    def save(self, address):
        context = super().save(address)
        self.update_virtual_alias_maps(address, context)
    
    def delete(self, address):
        context = super().delete(address)
        self.exclude_virtual_alias_maps(context)
    
    def commit(self):
        context = self.get_context_files()
        self.append(textwrap.dedent("""
            # Apply changes if needed
            [[ $UPDATED_VIRTUAL_ALIAS_DOMAINS == 1 ]] && {
                service postfix reload
            }
            [[ $UPDATED_VIRTUAL_ALIAS_MAPS == 1 ]] && {
                postmap %(virtual_alias_maps)s
            }
            exit $exit_code
            """) % context
        )


class AutoresponseController(ServiceController):
    """
    WARNING: not implemented
    """
    verbose_name = _("Mail autoresponse")
    model = 'mailboxes.Autoresponse'


class DovecotMaildirDisk(ServiceMonitor):
    """
    Maildir disk usage based on Dovecot maildirsize file
    http://wiki2.dovecot.org/Quota/Maildir
    """
    model = 'mailboxes.Mailbox'
    resource = ServiceMonitor.DISK
    verbose_name = _("Dovecot Maildir size")
    delete_old_equal_values = True
    doc_settings = (settings,
        ('MAILBOXES_MAILDIRSIZE_PATH',)
    )
    
    def prepare(self):
        super().prepare()
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


class PostfixMailscannerTraffic(ServiceMonitor):
    """
    A high-performance log parser.
    Reads the mail.log file only once, for all users.
    """
    model = 'mailboxes.Mailbox'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _("Postfix-Mailscanner traffic")
    script_executable = '/usr/bin/python'
    monthly_sum_old_values = True
    doc_settings = (settings,
        ('MAILBOXES_MAIL_LOG_PATH',)
    )
    
    def prepare(self):
        mail_log = settings.MAILBOXES_MAIL_LOG_PATH
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
            months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
            months = dict((m, '%02d' % n) for n, m in enumerate(months, 1))
            
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
                                        targets[req_id] = (username, 0)
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
                        sys.stderr.write(str(e)+'\\n')
                    
                for username, opts in users.iteritems():
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
        context = {
            'mailbox': mailbox.name,
            'object_id': mailbox.pk,
            'last_date': self.get_last_date(mailbox.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
        }
        return context

class RoundcubeIdentityController(ServiceController):
    """
    WARNING: not implemented
    """
    verbose_name = _("Roundcube Identity Controller")
    model = 'mailboxes.Mailbox'

