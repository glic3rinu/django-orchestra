import crypt
import os
import textwrap
from urllib.parse import urlparse

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController
from orchestra.utils.python import random_ascii

from . import ApacheTrafficByHost
from .. import settings


class DokuWikiMuController(ServiceController):
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
        self.append(textwrap.dedent("""\
            # Update custom domain link
            find %(farm_path)s \\
                -maxdepth 1 \\
                -type l \\
                -exec bash -c '
                    if [[ $(readlink {}) == "%(domain)s" && $(basename {}) != "%(custom_domain)s" ]]; then
                        rm {}
                    fi' \;\
            """) % context
        )
        if context['custom_domain']:
            self.append(textwrap.dedent("""\
                if [[ ! -e %(farm_path)s/%(custom_domain)s ]]; then
                    ln -s %(domain)s %(farm_path)s/%(custom_domain)s
                    chown -h %(user)s:%(group) %(farm_path)s/%(custom_domain)s
                fi""") % context
            )
    
    def delete(self, saas):
        context = self.get_context(saas)
        self.append("rm -fr %(app_path)s" % context)
        self.append(textwrap.dedent("""\
            # Delete custom domain link
            find %(farm_path)s \\
                -maxdepth 1 \\
                -type l \\
                -exec bash -c '
                    if [[ $(readlink {}) == "%(domain)s" ]]; then
                        rm {}
                    fi' \;\
            """) % context
        )
    
    def get_context(self, saas):
        context = super(DokuWikiMuController, self).get_context(saas)
        domain = saas.get_site_domain()
        context.update({
            'template': settings.SAAS_DOKUWIKI_TEMPLATE_PATH,
            'farm_path': os.path.normpath(settings.SAAS_DOKUWIKI_FARM_PATH),
            'app_path': os.path.join(settings.SAAS_DOKUWIKI_FARM_PATH, domain),
            'user': settings.SAAS_DOKUWIKI_USER,
            'group': settings.SAAS_DOKUWIKI_GROUP,
            'email': saas.account.email,
            'custom_url': saas.custom_url,
            'domain': domain,
        })
        if saas.custom_url:
            custom_url = urlparse(saas.custom_url)
            context.update({
                'custom_domain': custom_url.netloc,
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
