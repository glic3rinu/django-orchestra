from django.utils.translation import ugettext_lazy as _

from orchestra.orchestration import ServiceBackend


class SystemUserFTPBackend(ServiceBackend):
    name = 'SystemUserFTP'
    verbose_name = _("System user FTP")
    model = 'webftpaccounts.WebFTPAccount'
    
    def save(self, ftp):
        context = self.get_context(ftp)
        self.append("id %(username)s || useradd %(username)s \\\n"
                    "  --shell /dev/null" % context)
        self.append('echo "%(username)s:%(password)s" | chpasswd' % context)
        self.append("mkdir -p %(home)s" % context)
        self.append("chown %(username)s.%(username)s %(home)s" % context)
    
    def delete(self, ftp):
        context = self.get_context(ftp)
        self.append("userdel %(username)s" % context)
    
    def get_context(self, ftp):
        return {
            'username': ftp.username,
            'password': ftp.password,
            'home': ftp.home
        }
