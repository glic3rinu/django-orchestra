import fnmatch
import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace
from orchestra.contrib.resources import ServiceMonitor

from . import settings


class UNIXUserController(ServiceController):
    """
    Basic UNIX system user/group support based on <tt>useradd</tt>, <tt>usermod</tt>, <tt>userdel</tt> and <tt>groupdel</tt>.
    Autodetects and uses ACL if available, for better permission management.
    """
    verbose_name = _("UNIX user")
    model = 'systemusers.SystemUser'
    actions = ('save', 'delete', 'set_permission', 'validate_paths_exist', 'create_link')
    doc_settings = (settings, (
        'SYSTEMUSERS_DEFAULT_GROUP_MEMBERS',
        'SYSTEMUSERS_MOVE_ON_DELETE_PATH',
        'SYSTEMUSERS_FORBIDDEN_PATHS'
    ))
    
    def save(self, user):
        context = self.get_context(user)
        if not context['user']:
            return
        if not user.active:
            self.append(textwrap.dedent("""
                #Just disable that user, if it exists
                if id %(user)s ; then
                    usermod %(user)s --password '%(password)s'
                fi
                """) % context)
            return        
        # TODO userd add will fail if %(user)s group already exists
        self.append(textwrap.dedent("""
            # Update/create user state for %(user)s
            if id %(user)s ; then
                usermod %(user)s --home '%(home)s' \\
                    --password '%(password)s' \\
                    --shell '%(shell)s' \\
                    --groups '%(groups)s'
            else
                useradd_code=0
                useradd %(user)s --home '%(home)s' \\
                    --password '%(password)s' \\
                    --shell '%(shell)s' \\
                    --groups '%(groups)s' || useradd_code=$?
                if [[ $useradd_code -eq 8 ]]; then
                    # User is logged in, kill and retry
                    pkill -u %(user)s; sleep 2
                    pkill -9 -u %(user)s; sleep 1
                    useradd %(user)s --home '%(home)s' \\
                        --password '%(password)s' \\
                        --shell '%(shell)s' \\
                        --groups '%(groups)s'
                elif [[ $useradd_code -ne 0 ]]; then
                    exit $useradd_code
                fi
            fi
            mkdir -p '%(base_home)s'
            chmod 750 '%(base_home)s'
        """) % context
        )
        if context['home'] != context['base_home']:
            self.append(textwrap.dedent("""\
                # Set extra permissions: %(user)s home is inside %(mainuser)s home
                if true; then
#                if mount | grep "^$(df %(home)s|grep '^/'|cut -d' ' -f1)\s" | grep acl > /dev/null; then
                    # Account group as the owner
                    chown %(mainuser)s:%(mainuser)s '%(home)s'
                    chmod g+s '%(home)s'
                    # Home access
                    setfacl -m u:%(user)s:--x '%(mainuser_home)s'
                    # Grant perms to future files within the directory
                    setfacl -m d:u:%(user)s:rwx '%(home)s'
                    # Grant access to main user
                    setfacl -m d:u:%(mainuser)s:rwx '%(home)s'
                else
                    chmod g+rxw %(home)s
                fi""") % context
            )
        else:
            self.append(textwrap.dedent("""\
                chown %(user)s:%(group)s '%(home)s'
                ls -A /etc/skel/ | while read line; do
                    if [[ ! -e "%(home)s/${line}" ]]; then
                        cp -a "/etc/skel/${line}" "%(home)s/${line}" && \\
                        chown -R %(user)s:%(group)s "%(home)s/${line}"
                    fi
                done
                """) % context
            )
        for member in settings.SYSTEMUSERS_DEFAULT_GROUP_MEMBERS:
            context['member'] = member
            self.append('usermod -a -G %(user)s %(member)s || exit_code=$?' % context)
        if not user.is_main:
            self.append('usermod -a -G %(user)s %(mainuser)s || exit_code=$?' % context)
    
    def delete(self, user):
        context = self.get_context(user)
        if not context['user']:
            return
        self.append(textwrap.dedent("""
            # Delete %(user)s user
            nohup bash -c 'sleep 2 && killall -u %(user)s -s KILL' &> /dev/null &
            killall -u %(user)s || true
            userdel %(user)s || exit_code=$?
            groupdel %(group)s || exit_code=$?\
            """) % context
        )
        if context['deleted_home']:
            self.append(textwrap.dedent("""\
                # Move home into SYSTEMUSERS_MOVE_ON_DELETE_PATH, nesting if exists.
                deleted_home="%(deleted_home)s"
                while [[ -e "$deleted_home" ]]; do
                    deleted_home="${deleted_home}/$(basename ${deleted_home})"
                done
                mv '%(base_home)s' "$deleted_home" || exit_code=$?
                """) % context
            )
        else:
            self.append("rm -fr -- '%(base_home)s'" % context)
    
    def grant_permissions(self, user, context):
        context['perms'] = user.set_perm_perms
        # Capital X adds execution permissions for directories, not files
        context['perms_X'] = context['perms'] + 'X'
        self.append(textwrap.dedent("""\
            # Grant execution permissions to every parent directory
            for access_path in %(access_paths)s; do
                # Preserve existing ACLs
                acl=$(getfacl -a "$access_path" | grep '^user:%(user)s:') && {
                    perms=$(echo "$acl" | cut -d':' -f3)
                    perms=$(echo "$perms" | cut -c 1,2)x
                    setfacl -m u:%(user)s:$perms "$access_path"
                } || setfacl -m u:%(user)s:--x "$access_path"
            done
            # Grant perms to existing files, excluding execution
            find '%(perm_to)s' -type f %(exclude_acl)s \\
                -exec setfacl -m u:%(user)s:%(perms)s {} \\;
            # Grant perms to extisting directories and set defaults for future content
            find '%(perm_to)s' -type d %(exclude_acl)s \\
                -exec setfacl -m u:%(user)s:%(perms_X)s -m d:u:%(user)s:%(perms_X)s {} \\;
            # Account group as the owner of new files
            chmod g+s '%(perm_to)s'""") % context
        )
        if not user.is_main:
            self.append(textwrap.dedent("""\
                # Grant access to main user
                find '%(perm_to)s' -type d %(exclude_acl)s \\
                    -exec setfacl -m d:u:%(mainuser)s:rwx {} \\;\
                """) % context
            )
    
    def revoke_permissions(self, user, context):
        revoke_perms = {
            'rw': '',
            'r': 'w',
            'w': 'r',
        }
        context.update({
            'perms': revoke_perms[user.set_perm_perms],
            'option': '-x' if user.set_perm_perms == 'rw' else '-m'
        })
        self.append(textwrap.dedent("""\
            # Revoke permissions
            find '%(perm_to)s' %(exclude_acl)s \\
                -exec setfacl %(option)s u:%(user)s:%(perms)s {} \\;\
            """) % context
        )
    
    def set_permission(self, user):
        context = self.get_context(user)
        context.update({
            'perm_action': user.set_perm_action,
            'perm_to': os.path.join(user.set_perm_base_home, user.set_perm_home_extension),
        })
        exclude_acl = []
        for exclude in settings.SYSTEMUSERS_FORBIDDEN_PATHS:
            context['exclude_acl'] = os.path.join(user.set_perm_base_home, exclude)
            exclude_acl.append('-not -path "%(exclude_acl)s"' % context)
        context['exclude_acl'] = ' \\\n    -a '.join(exclude_acl) if exclude_acl else ''
        # Access paths
        head = user.set_perm_base_home
        relative = ''
        access_paths = ["'%s'" % head]
        for tail in user.set_perm_home_extension.split(os.sep)[:-1]:
            relative = os.path.join(relative, tail)
            for exclude in settings.SYSTEMUSERS_FORBIDDEN_PATHS:
                if fnmatch.fnmatch(relative, exclude):
                    break
            else:
                # No match
                head = os.path.join(head, tail)
                access_paths.append("'%s'" % head)
        context['access_paths'] = ' '.join(access_paths)
        
        if user.set_perm_action == 'grant':
            self.grant_permissions(user, context)
        elif user.set_perm_action == 'revoke':
            self.revoke_permissions(user, context)
        else:
            raise NotImplementedError()
    
    def create_link(self, user):
        context = self.get_context(user)
        context.update({
            'link_target': user.create_link_target,
            'link_name': user.create_link_name,
        })
        self.append(textwrap.dedent("""\
            # Create link
            su - %(user)s --shell /bin/bash << 'EOF' || exit_code=1
                if [[ ! -e '%(link_name)s' ]]; then
                    ln -s '%(link_target)s' '%(link_name)s'
                else
                    echo "%(link_name)s already exists, doing nothing." >&2
                    exit 1
                fi
            EOF""") % context
        )
    
    def validate_paths_exist(self, user):
        for path in user.paths_to_validate:
            context = {
                'path': path,
            }
            self.append(textwrap.dedent("""
                if [[ ! -e '%(path)s' ]]; then
                    echo "%(path)s path does not exists." >&2
                fi""") % context
            )
    
    def get_groups(self, user):
        if user.is_main:
            return user.account.systemusers.exclude(username=user.username).values_list('username', flat=True)
        return list(user.groups.values_list('username', flat=True))
    
    def get_context(self, user):
        context = {
            'object_id': user.pk,
            'user': user.username,
            'group': user.username,
            'groups': ','.join(self.get_groups(user)),
            'password': user.password if user.active else '*%s' % user.password,
            'shell': user.shell,
            'mainuser': user.username if user.is_main else user.account.username,
            'home': user.get_home(),
            'base_home': user.get_base_home(),
            'mainuser_home': user.main.get_home(),
        }
        context['deleted_home'] = settings.SYSTEMUSERS_MOVE_ON_DELETE_PATH % context
        return replace(context, "'", '"')


class UNIXUserDisk(ServiceMonitor):
    """
    <tt>du -bs &lt;home&gt;</tt>
    """
    model = 'systemusers.SystemUser'
    resource = ServiceMonitor.DISK
    verbose_name = _('UNIX user disk')
    delete_old_equal_values = True
    
    def prepare(self):
        super(UNIXUserDisk, self).prepare()
        self.append(textwrap.dedent("""\
            function monitor () {
                { SIZE=$(du -bs "$1") && echo $SIZE || echo 0; } | awk {'print $1'}
            }"""
        ))
    
    def monitor(self, user):
        context = self.get_context(user)
        self.append("echo %(object_id)s $(monitor %(base_home)s)" % context)
    
    def get_context(self, user):
        context = {
            'object_id': user.pk,
            'base_home': user.get_base_home(),
        }
        return replace(context, "'", '"')


class Exim4Traffic(ServiceMonitor):
    """
    Exim4 mainlog parser for mails sent on the webserver by system users (e.g. via PHP <tt>mail()</tt>)
    """
    model = 'systemusers.SystemUser'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _("Exim4 traffic")
    script_executable = '/usr/bin/python'
    monthly_sum_old_values = True
    doc_settings = (settings,
        ('SYSTEMUSERS_MAIL_LOG_PATH',)
    )
    
    def prepare(self):
        mainlog = settings.SYSTEMUSERS_MAIL_LOG_PATH
        context = {
            'current_date': self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'mainlogs': str((mainlog, mainlog+'.1')),
        }
        self.append(textwrap.dedent("""\
            import re
            import sys
            from datetime import datetime
            from dateutil import tz
            
            def to_local_timezone(date, tzlocal=tz.tzlocal()):
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
                date = date.replace(tzinfo=tz.tzutc())
                date = date.astimezone(tzlocal)
                return date
            
            mainlogs = {mainlogs}
            # Use local timezone
            end_date = to_local_timezone('{current_date}')
            end_date = int(end_date.strftime('%Y%m%d%H%M%S'))
            users = {{}}
            
            def prepare(object_id, username, ini_date):
                global users
                ini_date = to_local_timezone(ini_date)
                ini_date = int(ini_date.strftime('%Y%m%d%H%M%S'))
                users[username] = [ini_date, object_id, 0]
            
            def monitor(users, end_date, mainlogs):
                user_regex = re.compile(r' U=([^ ]+) ')
                for mainlog in mainlogs:
                    try:
                        with open(mainlog, 'r') as mainlog:
                            for line in mainlog.readlines():
                                if ' <= ' in line and 'P=local' in line:
                                    username = user_regex.search(line).groups()[0]
                                    try:
                                        sender = users[username]
                                    except KeyError:
                                        continue
                                    else:
                                        date, time, id, __, __, user, protocol, size = line.split()[:8]
                                        date = date.replace('-', '')
                                        date += time.replace(':', '')
                                        if sender[0] < int(date) < end_date:
                                            sender[2] += int(size[2:])
                    except IOError as e:
                        sys.stderr.write(str(e))
                
                for username, opts in users.iteritems():
                    __, object_id, size = opts
                    print object_id, size
            """).format(**context)
        )
    
    def commit(self):
        self.append('monitor(users, end_date, mainlogs)')
    
    def monitor(self, user):
        context = self.get_context(user)
        self.append("prepare(%(object_id)s, '%(username)s', '%(last_date)s')" % context)
    
    def get_context(self, user):
        context = {
            'username': user.username,
            'object_id': user.pk,
            'last_date': self.get_last_date(user.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
        }
        return context


class VsFTPdTraffic(ServiceMonitor):
    """
    vsFTPd log parser.
    """
    model = 'systemusers.SystemUser'
    resource = ServiceMonitor.TRAFFIC
    verbose_name = _('VsFTPd traffic')
    script_executable = '/usr/bin/python'
    monthly_sum_old_values = True
    doc_settings = (settings,
        ('SYSTEMUSERS_FTP_LOG_PATH',)
    )
    
    def prepare(self):
        vsftplog = settings.SYSTEMUSERS_FTP_LOG_PATH
        context = {
            'current_date': self.current_date.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'vsftplogs': str((vsftplog, vsftplog+'.1')),
        }
        self.append(textwrap.dedent("""\
            import re
            import sys
            from datetime import datetime
            from dateutil import tz
            
            def to_local_timezone(date, tzlocal=tz.tzlocal()):
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S %Z')
                date = date.replace(tzinfo=tz.tzutc())
                date = date.astimezone(tzlocal)
                return date
            
            vsftplogs = {vsftplogs}
            # Use local timezone
            end_date = to_local_timezone('{current_date}')
            end_date = int(end_date.strftime('%Y%m%d%H%M%S'))
            users = {{}}
            months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
            months = dict((m, '%02d' % n) for n, m in enumerate(months, 1))
            
            def prepare(object_id, username, ini_date):
                global users
                ini_date = to_local_timezone(ini_date)
                ini_date = int(ini_date.strftime('%Y%m%d%H%M%S'))
                users[username] = [ini_date, object_id, 0]
            
            def monitor(users, end_date, months, vsftplogs):
                user_regex = re.compile(r'\] \[([^ ]+)\] (OK|FAIL) ')
                bytes_regex = re.compile(r', ([0-9]+) bytes, ')
                for vsftplog in vsftplogs:
                    try:
                        with open(vsftplog, 'r') as vsftplog:
                            for line in vsftplog.readlines():
                                if ' bytes, ' in line:
                                    username = user_regex.search(line).groups()[0]
                                    try:
                                        user = users[username]
                                    except KeyError:
                                        continue
                                    else:
                                        __, month, day, time, year = line.split()[:5]
                                        date = year + months[month] + day + time.replace(':', '')
                                        if user[0] < int(date) < end_date:
                                            bytes = bytes_regex.search(line).groups()[0]
                                            user[2] += int(bytes)
                    except IOError as e:
                        sys.stderr.write(str(e))
                
                for username, opts in users.items():
                    __, object_id, size = opts
                    print object_id, size
            """).format(**context)
        )
    
    def monitor(self, user):
        context = self.get_context(user)
        self.append("prepare(%(object_id)s, '%(username)s', '%(last_date)s')" % context)
    
    def commit(self):
        self.append('monitor(users, end_date, months, vsftplogs)')
    
    def get_context(self, user):
        context = {
            'last_date': self.get_last_date(user.pk).strftime("%Y-%m-%d %H:%M:%S %Z"),
            'object_id': user.pk,
            'username': user.username,
        }
        return replace(context, "'", '"')
