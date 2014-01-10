from optparse import make_option
from os.path import expanduser

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.six.moves import input

from orchestra.utils.paths import get_project_root, get_site_root, get_project_name
from orchestra.utils.system import run, check_root, get_default_celeryd_username


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--user', dest='user', default=get_default_celeryd_username(),
                help='uWSGI daemon user.'),
            make_option('--group', dest='group', default='',
                help='uWSGI daemon group.'),
            make_option('--processes', dest='processes', default=4,
                help='uWSGI number of processes.'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleeryd process owner, which is the user how will perform tincd updates'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Configures nginx + uwsgi to run with your Orchestra instance.'
    
    @check_root
    def handle(self, *args, **options):
        interactive = options.get('interactive')
        
        context = {
            'project_name': get_project_name(),
            'project_root': get_project_root(),
            'site_root': get_site_root(),
            'media_root': settings.MEDIA_ROOT,
            'static_root': settings.STATIC_ROOT,
            'user': options.get('user'),
            'group': options.get('group') or options.get('user'),
            'home': expanduser("~%s" % options.get('user')),
            'processes': int(options.get('processes')),}
        
        nginx_conf = (
            'server {\n'
            '    listen 80;\n'
            '    listen [::]:80 ipv6only=on;\n'
            '    rewrite ^/$ /admin;\n'
            '    client_max_body_size 500m;\n'
            '    location / {\n'
            '        uwsgi_pass unix:///var/run/uwsgi/app/%(project_name)s/socket;\n'
            '        include uwsgi_params;\n'
            '    }\n'
            '    location /media  {\n'
            '        alias %(media_root)s;\n'
            '        expires 30d;\n'
            '    }\n'
            '    location /static {\n'
            '        alias %(static_root)s;\n'
            '        expires 30d;\n'
            '    }\n'
            '}\n') % context
        
        uwsgi_conf = (
            '[uwsgi]\n'
            'plugins      = python\n'
            'chdir        = %(site_root)s\n'
            'module       = %(project_name)s.wsgi\n'
            'master       = true\n'
            'processes    = %(processes)d\n'
            'chmod-socket = 664\n'
            'stats        = /run/uwsgi/%%(deb-confnamespace)/%%(deb-confname)/statsocket\n'
            'vacuum       = true\n'
            'uid          = %(user)s\n'
            'gid          = %(group)s\n'
            'env          = HOME=%(home)s\n') % context
        
        nginx = {
            'file': '/etc/nginx/conf.d/%(project_name)s.conf' % context,
            'conf': nginx_conf }
        uwsgi = {
            'file': '/etc/uwsgi/apps-available/%(project_name)s.ini' % context,
            'conf': uwsgi_conf }
        
        for extra_context in (nginx, uwsgi):
            context.update(extra_context)
            diff = run("echo '%(conf)s'|diff - %(file)s" % context, err_codes=[0,1,2])
            if diff.return_code == 2:
                # File does not exist
                run("echo '%(conf)s' > %(file)s" % context)
            elif diff.return_code == 1:
                # File is different, save the old one
                if interactive:
                    msg = ("\n\nFile %(file)s be updated, do you like to overide "
                           "it? (yes/no): " % context)
                    confirm = input(msg)
                    while 1:
                        if confirm not in ('yes', 'no'):
                            confirm = input('Please enter either "yes" or "no": ')
                            continue
                        if confirm == 'no':
                            return
                        break
                run("cp %(file)s %(file)s.save" % context)
                run("echo '%(conf)s' > %(file)s" % context)
                self.stdout.write("\033[1;31mA new version of %(file)s has been installed.\n "
                    "The old version has been placed at %(file)s.save\033[m" % context)
        
        run('ln -s /etc/uwsgi/apps-available/%(project_name)s.ini /etc/uwsgi/apps-enabled/' % context, err_codes=[0,1])
        
        # nginx should start after tincd
        current = "\$local_fs \$remote_fs \$network \$syslog"
        run('sed -i "s/  %s$/  %s \$named/g" /etc/init.d/nginx' % (current, current))
        
        rotate = (
            '/var/log/nginx/*.log {\n'
            '    daily\n'
            '    missingok\n'
            '    rotate 30\n'
            '    compress\n'
            '    delaycompress\n'
            '    notifempty\n'
            '    create 640 root adm\n'
            '    sharedscripts\n'
            '    postrotate\n'
            '        [ ! -f /var/run/nginx.pid ] || kill -USR1 `cat /var/run/nginx.pid`\n'
            '    endscript\n'
            '}\n')
        run("echo '%s' > /etc/logrotate.d/nginx" % rotate)
        
        # Allow nginx to write to uwsgi socket
        run('adduser www-data %(group)s' % context)
