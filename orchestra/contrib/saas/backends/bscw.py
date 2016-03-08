import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace

from .. import settings


class BSCWController(ServiceController):
    verbose_name = _("BSCW SaaS")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'bscw'"
    actions = ('save', 'delete', 'validate_creation')
    doc_settings = (settings,
        ('SAAS_BSCW_BSADMIN_PATH',)
    )
    
    def validate_creation(self, saas):
        context = self.get_context(saas)
        self.append(textwrap.dedent("""\
            if [[ $(%(bsadmin)s register %(email)s) ]]; then
                echo 'ValidationError: email-exists'
            fi
            if [[ $(%(bsadmin)s users -n %(username)s) ]]; then
                echo 'ValidationError: user-exists'
            fi""") % context
        )
    
    def save(self, saas):
        context = self.get_context(saas)
        if hasattr(saas, 'password'):
            self.append(textwrap.dedent("""\
                if [[ ! $(%(bsadmin)s register %(email)s) && ! $(%(bsadmin)s users -n %(username)s) ]]; then
                    # Create new user
                    %(bsadmin)s register -r %(email)s %(username)s '%(password)s'
                else
                    # Change password
                    %(bsadmin)s chpwd %(username)s '%(password)s'
                fi
                """) % context
            )
        elif saas.active:
            self.append("%(bsadmin)s chpwd -u %(username)s" % context)
        else:
            self.append("%(bsadmin)s chpwd -l %(username)s" % context)
    
    def delete(self, saas):
        context = self.get_context(saas)
        self.append("%(bsadmin)s rmuser -n %(username)s" % context)
    
    def get_context(self, saas):
        context = {
            'bsadmin': settings.SAAS_BSCW_BSADMIN_PATH,
            'email': saas.data.get('email'),
            'username': saas.name,
            'password': getattr(saas, 'password', None),
        }
        return replace(context, "'", '"')
