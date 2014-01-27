from django.utils.translation import ugettext_lazy as _

from orchestra.core.backends import ServiceBackend


class SystemUserFTPBackend(ServiceBackend):
    name = 'SystemUserFTP'
    verbose_name = _("System user FTP")
    models = ['ftp.FTP']
    
    def save(self, ftp):
        context = {
            'username': ftp.username,
            'password': ftp.password,
            'home': ftp.home
        }
        self.append("id %(username)s || useradd %(username)s"
                    "  --password %(password)s"
                    "  --home-dir %(home)s --create-home"
                    "  --shell SHELL /dev/null" % context)
    
    def delete(self, ftp):
        self.append("userdel %s" % ftp.username)
