import os
import textwrap

from orchestra.contrib.orchestration import ServiceController

from . import settings


class LetsEncryptController(ServiceController):
    model = 'websites.Website'
    verbose_name = "Let's encrypt!"
    actions = ('encrypt',)
    
    def prepare(self):
        super().prepare()
        self.cleanup = []
        context = {
            'letsencrypt_auto': settings.LETSENCRYPT_AUTO_PATH,
        }
        self.append(textwrap.dedent("""
            %(letsencrypt_auto)s --non-interactive --no-self-upgrade \\
                --keep --expand --agree-tos certonly --webroot \\""") % context
        )
    
    def encrypt(self, website):
        context = self.get_context(website)
        self.append("    --webroot-path %(webroot)s \\" % context)
        self.append("        --email %(email)s \\" % context)
        self.append("        -d %(domains)s \\" % context)
        self.cleanup.append("rm -rf -- %(webroot)s/.well-known" % context)
    
    def commit(self):
        self.append("    || exit_code=$?")
        for cleanup in self.cleanup:
            self.append(cleanup)
        context = {
            'letsencrypt_live': os.path.normpath(settings.LETSENCRYPT_LIVE_PATH),
        }
        self.append(textwrap.dedent("""
            # Report back the lineages in order to infere each certificate path
            echo '<live-lineages>'
            find %(letsencrypt_live)s/* -maxdepth 0
            echo '</live-lineages>'""") % context
        )
        super().commit()
    
    def get_context(self, website):
        content = website.content_set.get(path='/')
        return {
            'letsencrypt_auto': settings.LETSENCRYPT_AUTO_PATH,
            'webroot': content.webapp.get_path(),
            'email': settings.LETSENCRYPT_EMAIL or website.account.email,
            'domains': ' \\\n        -d '.join(website.encrypt_domains),
        }
