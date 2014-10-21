import re
import textwrap

from django.utils import timezone
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
                }""" % context
            ))
    
    def exclude_virtual_alias_domain(self, context):
        address_domain = context['address_domain']
        if not List.objects.filter(address_domain=address_domain).exists():
            self.append('sed -i "/^%(address_domain)s\s*/d" %(virtual_alias_domains)s' % context)
    
    def get_virtual_aliases(self, context):
        aliases = []
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
            }""" % context))
        # Custom domain
        if mail_list.address:
            aliases = self.get_virtual_aliases(context)
            # Preserve indentation
            spaces = '    '*4
            context['aliases'] = spaces + aliases.replace('\n', '\n'+spaces)
            self.append(textwrap.dedent("""\
                if [[ ! $(grep '\s\s*%(name)s\s*$' %(virtual_alias)s) ]]; then
                    echo '# %(banner)s\n%(aliases)s
                    ' >> %(virtual_alias)s
                    UPDATED_VIRTUAL_ALIAS=1
                else
                    if [[ ! $(grep '^\s*%(address_name)s@%(address_domain)s\s\s*%(name)s\s*$' %(virtual_alias)s) ]]; then
                        sed -i "s/^.*\s%(name)s\s*$//" %(virtual_alias)s
                        echo '# %(banner)s\n%(aliases)s
                        ' >> %(virtual_alias)s
                        UPDATED_VIRTUAL_ALIAS=1
                    fi
                fi""" % context
            ))
            self.append('echo "require_explicit_destination = 0" | '
                        '%(mailman_root)s/bin/config_list -i /dev/stdin %(name)s' % context)
            self.append(textwrap.dedent("""\
                echo "host_name = '%(address_domain)s'" | \
                    %(mailman_root)s/bin/config_list -i /dev/stdin %(name)s""" % context))
        else:
            # Cleanup shit
            self.append(textwrap.dedent("""\
                if [[ ! $(grep '\s\s*%(name)s\s*$' %(virtual_alias)s) ]]; then
                    sed -i "s/^.*\s%(name)s\s*$//" %(virtual_alias)s
                fi""" % context
            ))
        # Update
        if context['password'] is not None:
            self.append('%(mailman_root)s/bin/change_pw --listname="%(name)s" --password="%(password)s"' % context)
        self.include_virtual_alias_domain(context)
    
    def delete(self, mail_list):
        context = self.get_context(mail_list)
        self.exclude_virtual_alias_domain(context)
        for address in self.addresses:
            context['address'] = address
            self.append('sed -i "s/^.*\s%(name)s%(address)s\s*$//" %(virtual_alias)s' % context)
        self.append("rmlist -a %(name)s" % context)
    
    def commit(self):
        context = self.get_context_files()
        self.append(textwrap.dedent("""
            [[ $UPDATED_VIRTUAL_ALIAS == 1 ]] && { postmap %(virtual_alias)s; }
            [[ $UPDATED_VIRTUAL_ALIAS_DOMAINS == 1 ]] && { /etc/init.d/postfix reload; }
            """ % context
        ))
    
    def get_context_files(self):
        return {
            'virtual_alias': settings.LISTS_VIRTUAL_ALIAS_PATH,
            'virtual_alias_domains': settings.LISTS_VIRTUAL_ALIAS_DOMAINS_PATH,
        }
    
    def get_context(self, mail_list):
        context = self.get_context_files()
        context.update({
            'banner': self.get_banner(),
            'name': mail_list.name,
            'password': mail_list.password,
            'domain': mail_list.address_domain or settings.LISTS_DEFAULT_DOMAIN,
            'address_name': mail_list.get_address_name,
            'address_domain': mail_list.address_domain,
            'admin': mail_list.admin_email,
            'mailman_root': settings.LISTS_MAILMAN_ROOT_PATH,
        })
        return context


class MailmanTraffic(ServiceMonitor):
    model = 'lists.List'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _("Mailman traffic")
    
    def prepare(self):
        current_date = timezone.localtime(self.current_date)
        current_date = current_date.strftime("%b %d %H:%M:%S")
        self.append(textwrap.dedent("""\
            function monitor () {
                OBJECT_ID=$1
                LAST_DATE=$2
                LIST_NAME="$3"
                MAILMAN_LOG="$4"
                
                SUBSCRIBERS=$(list_members ${LIST_NAME} | wc -l)
                SIZE=$(grep ' post to ${LIST_NAME} ' "${MAILMAN_LOG}" \\
                       | awk '"$LAST_DATE"<=$0 && $0<="%s"' \\
                       | sed 's/.*size=\([0-9]*\).*/\\1/' \\
                       | tr '\\n' '+' \\
                       | xargs -i echo {} )
                echo ${OBJECT_ID} $(( ${SIZE}*${SUBSCRIBERS} ))
            }""" % current_date))
    
    def monitor(self, mail_list):
        context = self.get_context(mail_list)
        self.append(
            'monitor %(object_id)i %(last_date)s "%(list_name)s" "%(log_file)s"' % context)
    
    def get_context(self, mail_list):
        last_date = timezone.localtime(self.get_last_date(mail_list.pk))
        return {
            'mailman_log': settings.LISTS_MAILMAN_POST_LOG_PATH,
            'list_name': mail_list.name,
            'object_id': mail_list.pk,
            'last_date': last_date.strftime("%b %d %H:%M:%S"),
        }


class MailmanTraffic(ServiceMonitor):
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
