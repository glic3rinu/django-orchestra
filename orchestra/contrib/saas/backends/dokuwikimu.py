import crypt
import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController
from orchestra.utils.python import random_ascii

from . import ApacheTrafficByHost
from .. import settings


class DokuWikiMuBackend(ServiceController):
    """
    Creates a DokuWiki site on a DokuWiki multisite installation.
    """
    name = 'dokuwiki'
    verbose_name = _("DokuWiki multisite")
    model = 'saas.SaaS'
    default_route_match = "saas.service == 'dokuwiki'"
    doc_settings = (settings, (
        'SAAS_DOKUWIKI_TEMPLATE_PATH',
        'SAAS_DOKUWIKI_FARM_PATH',
        'SAAS_DOKUWIKI_USER',
        'SAAS_DOKUWIKI_GROUP',
    ))
    
    def save(self, saas):
        context = self.get_context(saas)
        self.append(textwrap.dedent("""
            if [[ ! -e %(app_path)s ]]; then
                mkdir %(app_path)s
                tar xfz %(template)s -C %(app_path)s
                chown -R %(user)s:%(group)s %(app_path)s
            fi""") % context
        )
        if context['password']:
            self.append(textwrap.dedent("""\
                if grep '^admin:' %(users_path)s > /dev/null; then
                    sed -i 's#^admin:.*$#admin:%(password)s:admin:%(email)s:admin,user#' %(users_path)s
                else
                    echo 'admin:%(password)s:admin:%(email)s:admin,user' >> %(users_path)s
                fi""") % context
            )
    
    def delete(self, saas):
        context = self.get_context(saas)
        self.append("rm -fr %(app_path)s" % context)
    
    def get_context(self, saas):
        context = super(DokuWikiMuBackend, self).get_context(saas)
        context.update({
            'template': settings.SAAS_DOKUWIKI_TEMPLATE_PATH,
            'farm_path': settings.SAAS_DOKUWIKI_FARM_PATH,
            'app_path': os.path.join(settings.SAAS_DOKUWIKI_FARM_PATH, saas.get_site_domain()),
            'user': settings.SAAS_DOKUWIKI_USER,
            'group': settings.SAAS_DOKUWIKI_GROUP,
            'email': saas.account.email,
        })
        password = getattr(saas, 'password', None)
        salt = random_ascii(8)
        context.update({
            'password': crypt.crypt(password, '$1$'+salt) if password else None,
            'users_path': os.path.join(context['app_path'], 'conf/users.auth.php'),
        })
        return context


class DokuWikiMuTraffic(ApacheTrafficByHost):
    __doc__ = ApacheTrafficByHost.__doc__
    verbose_name = _("DokuWiki MU Traffic")
    default_route_match = "saas.service == 'dokuwiki'"
    doc_settings = (settings,
        ('SAAS_TRAFFIC_IGNORE_HOSTS', 'SAAS_DOKUWIKI_LOG_PATH')
    )
    log_path = settings.SAAS_DOKUWIKI_LOG_PATH
