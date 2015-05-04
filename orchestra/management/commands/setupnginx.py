import textwrap
from optparse import make_option
from os.path import expanduser

from django.conf import settings
from django.core.management.base import BaseCommand

from orchestra.utils import paths
from orchestra.utils.sys import run, check_root, get_default_celeryd_username


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--cert', dest='cert', default='',
                help='Nginx SSL certificate, one will be created by default.'),
            make_option('--cert-key', dest='cert_key', default='',
                help='Nginx SSL certificate key.'),
            make_option('--server-name', dest='server_name', default='',
                help='Nginx SSL certificate key.'),
            make_option('--user', dest='user', default='',
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
        
        cert = options.get('cert')
        cert_key = options.get('cert_key')
        if bool(cert) != bool(cert_key):
            raise CommandError("--cert and --cert-key go in tandem")
        
        if not cert:
            run("mkdir -p /etc/nginx/ssl")
            if interactive:
                run("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt")
        
        context = {
            'project_name': paths.get_project_name(),
            'project_dir': paths.get_project_dir(),
            'site_dir': paths.get_site_dir(),
            'static_root': settings.STATIC_ROOT,
            'user': options.get('user'),
            'group': options.get('group') or options.get('user'),
            'home': expanduser("~%s" % options.get('user')),
            'processes': int(options.get('processes')),}
        
        nginx_conf = textwrap.dedent("""\
            server {
                listen 80;
                listen [::]:80 ipv6only=on;
                rewrite ^/$ /admin/;
                client_max_body_size 500m;
                location / {
                    uwsgi_pass unix:///var/run/uwsgi/app/%(project_name)s/socket;
                    include uwsgi_params;
                }
                location /static {
                    alias %(static_root)s;
                    expires 30d;
                }
            }
            """
        ) % context
        
        uwsgi_conf = textwrap.dedent("""\
            [uwsgi]
            plugins      = python
            chdir        = %(site_dir)s
            module       = %(project_name)s.wsgi
            master       = true
            processes    = %(processes)d
            chmod-socket = 664
            stats        = /run/uwsgi/%%(deb-confnamespace)/%%(deb-confname)/statsocket
            vacuum       = true
            uid          = %(user)s
            gid          = %(group)s
            env          = HOME=%(home)s
            touch-reload = %(project_dir)s/wsgi.py
            """
        ) % context
        
        nginx = {
            'file': '/etc/nginx/conf.d/%(project_name)s.conf' % context,
            'conf': nginx_conf }
        uwsgi = {
            'file': '/etc/uwsgi/apps-available/%(project_name)s.ini' % context,
            'conf': uwsgi_conf }
        
        for extra_context in (nginx, uwsgi):
            context.update(extra_context)
            diff = run("echo '%(conf)s'|diff - %(file)s" % context, error_codes=[0,1,2])
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
        
        run('ln -s /etc/uwsgi/apps-available/%(project_name)s.ini /etc/uwsgi/apps-enabled/' % context, error_codes=[0,1])
        
        # nginx should start after tincd
        current = "\$local_fs \$remote_fs \$network \$syslog"
        run('sed -i "s/  %s$/  %s \$named/g" /etc/init.d/nginx' % (current, current))
        
        rotate = textwrap.dedent("""\
            /var/log/nginx/*.log {
                daily
                missingok
                rotate 30
                compress
                delaycompress
                notifempty
                create 640 root adm
                sharedscripts
                postrotate
                    [ ! -f /var/run/nginx.pid ] || kill -USR1 `cat /var/run/nginx.pid`
                endscript
            }"""
        )
        run("echo '%s' > /etc/logrotate.d/nginx" % rotate)
        
        # Allow nginx to write to uwsgi socket
        run('adduser www-data %(group)s' % context)
