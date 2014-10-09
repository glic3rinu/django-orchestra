import textwrap

from django.utils import timezone

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from . import settings
from .models import List


class MailmanBackend(ServiceController):
    verbose_name = "Mailman"
    model = 'lists.List'
    
    def include_virtual_alias_domain(self, context):
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
        for address in addresses:
            context['address'] = address
            aliases.append("%(address_name)s%(address)s@%(domain)s\t%(name)s%(address)s" % context)
        return '\n'.join(aliases)
    
    def save(self, mail_list):
        if not getattr(mail_list, 'password', None):
            # TODO
            # Create only support for now
            return
        context = self.get_context(mail_list)
        self.append("newlist --quiet --emailhost='%(domain)s' '%(name)s' '%(admin)s' '%(password)s'" % context)
        if mail_list.address:
            context['aliases'] = self.get_virtual_aliases(context)
            self.append(
                "if [[ ! $(grep '^\s*%(name)s\s' %(virtual_alias)s) ]]; then\n"
                "   echo '# %(banner)s\n%(aliases)s\n' >> %(virtual_alias)s\n"
                "   UPDATED_VIRTUAL_ALIAS=1\n"
                "fi" % context
            )
        self.include_virtual_alias_domain(context)
    
    def delete(self, mail_list):
        pass
    
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
            'virtual_alias_domains': settings.MAILS_VIRTUAL_ALIAS_DOMAINS_PATH,
        }
    
    def get_context(self, mail_list):
        context = self.get_context_files()
        context.update({
            'banner': self.get_banner(),
            'name': mail_list.name,
            'password': mail_list.password,
            'domain': mail_list.address_domain or settings.LISTS_DEFAULT_DOMAIN,
            'address_name': mail_list.address_name,
            'address_domain': mail_list.address_domain,
            'admin': mail_list.admin_email,
        })
        return context


class MailmanTraffic(ServiceMonitor):
    model = 'lists.List'
    resource = ServiceMonitor.TRAFFIC
    
    def prepare(self):
        current_date = timezone.localtime(self.current_date)
        current_date = current_date.strftime("%b %d %H:%M:%S")
        self.append(textwrap.dedent("""
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
