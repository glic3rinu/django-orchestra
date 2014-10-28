import logging
import textwrap
import os

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from . import settings
from .models import Address

# TODO http://wiki2.dovecot.org/HowTo/SimpleVirtualInstall
# TODO http://wiki2.dovecot.org/HowTo/VirtualUserFlatFilesPostfix
# TODO mount the filesystem with "nosuid" option


logger = logging.getLogger(__name__)


class PasswdVirtualUserBackend(ServiceController):
    verbose_name = _("Mail virtual user (passwd-file)")
    model = 'mailboxes.Mailbox'
    # TODO related_models = ('resources__content_type') ?? needed for updating disk usage from resource.data
    
    DEFAULT_GROUP = 'postfix'
    
    def set_user(self, context):
        self.append(textwrap.dedent("""
            if [[ $( grep "^%(username)s:" %(passwd_path)s ) ]]; then
               sed -i 's#^%(username)s:.*#%(passwd)s#' %(passwd_path)s
            else
               echo '%(passwd)s' >> %(passwd_path)s
            fi""" % context
        ))
        self.append("mkdir -p %(home)s" % context)
        self.append("chown %(uid)s.%(gid)s %(home)s" % context)
    
    def set_mailbox(self, context):
        self.append(textwrap.dedent("""
            if [[ ! $(grep "^%(username)s@%(mailbox_domain)s\s" %(virtual_mailbox_maps)s) ]]; then
                echo "%(username)s@%(mailbox_domain)s\tOK" >> %(virtual_mailbox_maps)s
                UPDATED_VIRTUAL_MAILBOX_MAPS=1
            fi""" % context))
    
    def generate_filter(self, mailbox, context):
        self.append("doveadm mailbox create -u %(username)s Spam" % context)
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
        self.append("sed -i '/^%(username)s:.*/d' %(passwd_path)s" % context)
        self.append("sed -i '/^%(username)s@%(mailbox_domain)s\s.*/d' %(virtual_mailbox_maps)s" % context)
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
        self.append(
            "[[ $UPDATED_VIRTUAL_MAILBOX_MAPS == 1 ]] && { postmap %(virtual_mailbox_maps)s; }"
             % context
        )
    
    def get_context(self, mailbox):
        context = {
            'name': mailbox.name,
            'username': mailbox.name,
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
        context['passwd'] = '{username}:{password}:{uid}:{gid}::{home}::{extra_fields}'.format(**context)
        return context


class PostfixAddressBackend(ServiceController):
    verbose_name = _("Postfix address")
    model = 'mailboxes.Address'
    
    def include_virtual_alias_domain(self, context):
        self.append(textwrap.dedent("""
            [[ $(grep "^\s*%(domain)s\s*$" %(virtual_alias_domains)s) ]] || {
                echo "%(domain)s" >> %(virtual_alias_domains)s
                UPDATED_VIRTUAL_ALIAS_DOMAINS=1
            }""" % context
        ))
    
    def exclude_virtual_alias_domain(self, context):
        domain = context['domain']
        if not Address.objects.filter(domain=domain).exists():
            self.append('sed -i "/^%(domain)s\s*/d" %(virtual_alias_domains)s' % context)
    
    def update_virtual_alias_maps(self, address, context):
        destination = []
        for mailbox in address.get_mailboxes():
            context['mailbox'] = mailbox
            destination.append("%(mailbox)s@%(mailbox_domain)s" % context)
        for forward in address.forward:
            if '@' in forward:
                destination.append(forward)
        if destination:
            context['destination'] = ' '.join(destination)
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
                fi""" % context
            ))
        else:
            logger.warning("Address %i is empty" % address.pk)
            self.append('sed -i "/^%(email)s\s/d" %(virtual_alias_maps)s')
            self.append('UPDATED_VIRTUAL_ALIAS_MAPS=1')
    
    def exclude_virtual_alias_maps(self, context):
        self.append(textwrap.dedent("""
            if [[ $(grep "^%(email)s\s" %(virtual_alias_maps)s) ]]; then
               sed -i "/^%(email)s\s.*$/d" %(virtual_alias_maps)s
               UPDATED_VIRTUAL_ALIAS_MAPS=1
            fi""" % context
        ))
    
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
            """ % context
        ))
    
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
    model = 'mailboxes.Mailbox'
    resource = ServiceMonitor.DISK
    verbose_name = _("Maildir disk usage")
    
    def monitor(self, mailbox):
        context = self.get_context(mailbox)
        self.append(
            "SIZE=$(sed -n '2p' %(maildir_path)s | cut -d' ' -f1)\n"
            "echo %(object_id)s ${SIZE:-0}" % context
        )
    
    def get_context(self, mailbox):
        home = mailbox.get_home()
        context = {
            'maildir_path': os.path.join(home, 'Maildir/maildirsize'),
            'object_id': mailbox.pk
        }
        return context
