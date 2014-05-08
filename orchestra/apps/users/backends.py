from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceBackend

from . import settings


class SystemUserBackend(ServiceBackend):
    verbose_name = _("System User")
    model = 'users.User'
    ignore_fields = ['last_login']

    def save(self, user):
        context = self.get_context(user)
        if user.is_main:
            self.append(
                "if [[ $( id %(username)s ) ]]; then \n"
                "   usermod --password '%(password)s' %(username)s \n"
                "else \n"
                "   useradd %(username)s --password '%(password)s' \\\n"
                "       --shell /bin/false \n"
                "fi" % context
            )
            self.append("mkdir -p %(home)s" % context)
            self.append("chown %(username)s.%(username)s %(home)s" % context)
        else:
            self.delete(user)
    
    def delete(self, user):
        context = self.get_context(user)
        self.append("{ sleep 2 && killall -u %(username)s -s KILL; } &" % context)
        self.append("killall -u %(username)s" % context)
        self.append("userdel %(username)s" % context)
    
    def get_context(self, user):
        context = {
            'username': user.username,
            'password': user.password if user.is_active else '*%s' % user.password,
        }
        context['home'] = settings.USERS_SYSTEMUSER_HOME % context
        return context
