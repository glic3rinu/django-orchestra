import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController
from orchestra.apps.resources import ServiceMonitor

from . import settings


class SystemUserBackend(ServiceController):
    verbose_name = _("System user")
    model = 'systemusers.SystemUser'
    actions = ('save', 'delete', 'grant_permission')
    
    def save(self, user):
        context = self.get_context(user)
        groups = ','.join(self.get_groups(user))
        context['groups_arg'] = '--groups %s' % groups if groups else ''
        self.append(textwrap.dedent("""
            if [[ $( id %(user)s ) ]]; then
               usermod  %(user)s --password '%(password)s' --shell %(shell)s %(groups_arg)s
            else
               useradd %(user)s --home %(home)s --password '%(password)s' --shell %(shell)s %(groups_arg)s
            fi
            mkdir -p %(home)s
            chmod 750 %(home)s
            chown %(user)s:%(user)s %(home)s""") % context
        )
        for member in settings.SYSTEMUSERS_DEFAULT_GROUP_MEMBERS:
            context['member'] = member
            self.append('usermod -a -G %(user)s %(member)s' % context)
        if not user.is_main:
            self.append('usermod -a -G %(user)s %(mainuser)s' % context)
    
    def delete(self, user):
        context = self.get_context(user)
        self.append(textwrap.dedent("""\
            { sleep 2 && killall -u %(user)s -s KILL; } &
            killall -u %(user)s || true
            userdel %(user)s || true
            groupdel %(group)s || true""") % context
        )
        self.delete_home(context, user)
    
    def grant_permission(self, user):
        context = self.get_context(user)
        # TODO setacl
    
    def delete_home(self, context, user):
        if user.home.rstrip('/') == user.get_base_home().rstrip('/'):
            # TODO delete instead of this shit
            self.append("mv %(home)s %(home)s.deleted" % context)
    
    def get_groups(self, user):
        if user.is_main:
            return user.account.systemusers.exclude(username=user.username).values_list('username', flat=True)
        return list(user.groups.values_list('username', flat=True))
    
    def get_context(self, user):
        context = {
            'object_id': user.pk,
            'user': user.username,
            'group': user.username,
            'password': user.password if user.active else '*%s' % user.password,
            'shell': user.shell,
            'mainuser': user.username if user.is_main else user.account.username,
            'home': user.get_home()
        }
        return context


class SystemUserDisk(ServiceMonitor):
    model = 'systemusers.SystemUser'
    resource = ServiceMonitor.DISK
    verbose_name = _('Systemuser disk')
    
    def prepare(self):
        super(SystemUserDisk, self).prepare()
        self.append(textwrap.dedent("""\
            function monitor () {
                { du -bs "$1" || echo 0; } | awk {'print $1'}
            }"""
        ))
    
    def monitor(self, user):
        context = self.get_context(user)
        if user.is_main or os.path.normpath(user.home) == user.get_base_home():
            self.append("echo %(object_id)s $(monitor %(home)s)" % context)
        else:
            # Home is already included in other user home
            self.append("echo %(object_id)s 0" % context)
    
    def get_context(self, user):
        return {
            'object_id': user.pk,
            'home': user.home,
        }


class FTPTraffic(ServiceMonitor):
    model = 'systemusers.SystemUser'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _('Systemuser FTP traffic')
    
    def prepare(self):
        super(FTPTraffic, self).prepare()
        current_date = self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z")
        self.append(textwrap.dedent("""\
            function monitor () {
                OBJECT_ID=$1
                INI_DATE=$(date "+%%Y%%m%%d%%H%%M%%S" -d "$2")
                END_DATE=$(date '+%%Y%%m%%d%%H%%M%%S' -d '%s')
                USERNAME="$3"
                LOG_FILE="$4"
                {
                    grep " bytes, " ${LOG_FILE} \\
                        | grep " \\[${USERNAME}\\] " \\
                        | awk -v ini="${INI_DATE}" -v end="${END_DATE}" '
                            BEGIN {
                                sum = 0
                                months["Jan"] = "01"
                                months["Feb"] = "02"
                                months["Mar"] = "03"
                                months["Apr"] = "04"
                                months["May"] = "05"
                                months["Jun"] = "06"
                                months["Jul"] = "07"
                                months["Aug"] = "08"
                                months["Sep"] = "09"
                                months["Oct"] = "10"
                                months["Nov"] = "11"
                                months["Dec"] = "12"
                            } {
                                # Fri Jul  1 13:23:17 2014
                                split($4, time, ":")
                                day = sprintf("%%02d", $3)
                                # line_date = year month day hour minute second
                                line_date = $5 months[$2] day time[1] time[2] time[3]
                                if ( line_date > ini && line_date < end) {
                                    sum += $(NF-2)
                                }
                            } END {
                                print sum
                            }' || [[ $? == 1 ]] && true
                } | xargs echo ${OBJECT_ID}
            }""") % current_date)
    
    def monitor(self, user):
        context = self.get_context(user)
        self.append(
            'monitor {object_id} "{last_date}" "{username}" {log_file}'.format(**context)
        )
    
    def get_context(self, user):
        return {
            'log_file': '%s{,.1}' % settings.SYSTEMUSERS_FTP_LOG_PATH,
            'last_date': self.get_last_date(user.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
            'object_id': user.pk,
            'username': user.username,
        }
