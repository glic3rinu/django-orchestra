import os
import textwrap
from optparse import make_option
from os.path import expanduser

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from orchestra.utils import paths
from orchestra.utils.sys import run, check_root, confirm


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--cert', dest='cert', default='',
                help='Nginx SSL certificate, one will be created by default.'),
            make_option('--cert-key', dest='cert_key', default='',
                help='Nginx SSL certificate key.'),
            
            make_option('--cert-path', dest='cert_path',
                default=os.path.join(paths.get_site_dir(), 'ssl', 'orchestra.crt'),
                help='Nginx SSL certificate, one will be created by default.'),
            make_option('--cert-key-path', dest='cert_key_path',
                default=os.path.join(paths.get_site_dir(), 'ssl', 'orchestra.key'),
                help='Nginx SSL certificate key.'),
            # Cert options
            make_option('--cert-override', dest='cert_override', action='store_true',
                default=False, help='Force override cert and keys if exists.'),
            make_option('--cert-country', dest='cert_country', default='ES',
                help='Certificate Distinguished Name Country.'),
            make_option('--cert-state', dest='cert_state', default='Spain',
                help='Certificate Distinguished Name STATE.'),
            make_option('--cert-locality', dest='cert_locality', default='Barcelona',
                help='Certificate Distinguished Name Country.'),
            make_option('--cert-org_name', dest='cert_org_name', default='Orchestra',
                help='Certificate Distinguished Name Organization Name.'),
            make_option('--cert-org_unit', dest='cert_org_unit', default='DevOps',
                help='Certificate Distinguished Name Organization Unity.'),
            make_option('--cert-email', dest='cert_email', default='orchestra@orchestra.lan',
                help='Certificate Distinguished Name Email Address.'),
            make_option('--cert-common_name', dest='cert_common_name', default=None,
                help='Certificate Distinguished Name Common Name.'),
            
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
    
    def generate_certificate(self, **options):
        override = options.get('cert_override')
        interactive = options.get('interactive')
        
        cert = options.get('cert')
        key = options.get('cert_key')
        if bool(cert) != bool(key):
            raise CommandError("--cert and --cert-key go in tandem")
        
        cert_path = options.get('cert_path')
        key_path = options.get('cert_key_path')
        
        run('mkdir -p %s' % os.path.dirname(cert_path))
        exists = os.path.isfile(cert_path)
        
        if not override and exists:
            self.stdout.write('Your cert and keys are already in place.')
            self.stdout.write('Use --override in order to regenerate them.')
            return cert_path, key_path
        
        common_name = options.get('cert_common_name') or options.get('server_name') or 'orchestra.lan'
        country = options.get('cert_country')
        state = options.get('cert_state')
        locality = options.get('cert_locality')
        org_name = options.get('cert_org_name')
        org_unit = options.get('cert_org_unit')
        email = options.get('cert_email')
        if interactive:
            msg = ('-----\n'
                'You are about to be asked to enter information that\n'
                'will be incorporated\n'
                'into your certificate request.\n'
                'What you are about to enter is what is called a\n'
                'Distinguished Name or a DN.\n'
                'There are quite a few fields but you can leave some blank\n'
                '-----\n')
            self.stdout.write(msg)
            
            msg = 'Country Name (2 letter code) [%s]: ' % country
            country = input(msg) or country
            
            msg = 'State or Province Name (full name) [%s]: ' % state
            state = input(msg) or state
            
            msg = 'Locality Name (eg, city) [%s]: ' % locality
            locality = input(msg) or locality
            
            msg = 'Organization Name (eg, company) [%s]: ' % org_name
            org_name = input(msg) or org_name
            
            msg = 'Organizational Unit Name (eg, section) [%s]: ' % org_unit
            org_unit = input(msg) or org_unit
            
            msg = 'Email Address [%s]: ' % email
            email = input(msg) or email
            
        self.stdout.write('Common Name: %s' % common_name)
        subject = {
            'C': country,
            'S': state,
            'L': locality,
            'O': org_name,
            'OU': org_unit,
            'Email': email,
            'CN': common_name,
        }
        context = {
            'subject': ''.join(('/%s=%s' % (k,v) for k,v in subject.items())),
            'key_path': key_path,
            'cert_path': cert_path,
            'cert_root': os.path.dirname(cert_path),
        }
        self.stdout.write('writing new cert to \'%s\'' % cert_path)
        self.stdout.write('writing new cert key to \'%s\'' % key_path)
        run(textwrap.dedent("""\
            openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout %(key_path)s -out %(cert_path)s -subj "%(subject)s"
            chown --reference=%(cert_root)s %(cert_path)s %(key_path)s\
            """) % context, display=True
        )
        return cert_path, key_path
    
    @check_root
    def handle(self, *args, **options):
        user = options.get('user')
        if not user:
            raise CommandError("System user for running uwsgi must be provided.")
        
        cert_path, key_path = self.generate_certificate(**options)
        server_name = options.get('server_name')
        
        context = {
            'cert_path': cert_path,
            'key_path': key_path,
            'project_name': paths.get_project_name(),
            'project_dir': paths.get_project_dir(),
            'site_dir': paths.get_site_dir(),
            'static_root': settings.STATIC_ROOT,
            'static_url': (settings.STATIC_URL or '/static').rstrip('/'),
            'user': user,
            'group': options.get('group') or user,
            'home': expanduser("~%s" % options.get('user')),
            'processes': int(options.get('processes')),
            'server_name': 'server_name %s' % server_name if server_name else ''
        }
        
        nginx_conf = textwrap.dedent("""\
            server {
                listen 80;
                listen [::]:80 ipv6only=on;
                return 301 https://$host$request_uri;
            }
            
            server {
                listen 443 ssl;
                # listen [::]:443 ssl; # add SSL support to IPv6 address
                %(server_name)s
                ssl_certificate %(cert_path)s;
                ssl_certificate_key %(key_path)s;
                rewrite ^/$ /admin/;
                client_max_body_size 16m;
                location / {
                    uwsgi_pass unix:///var/run/uwsgi/app/%(project_name)s/socket;
                    include uwsgi_params;
                }
                location %(static_url)s {
                    alias %(static_root)s;
                    expires 30d;
                }
            }
            """
        ) % context
        
        uwsgi_conf = textwrap.dedent("""\
            [uwsgi]
            plugins        = python3
            chdir          = %(site_dir)s
            module         = %(project_name)s.wsgi
            master         = true
            workers        = %(processes)d
            chmod-socket   = 664
            stats          = /run/uwsgi/%%(deb-confnamespace)/%%(deb-confname)/statsocket
            uid            = %(user)s
            gid            = %(group)s
            env            = HOME=%(home)s
            touch-reload   = %(project_dir)s/wsgi.py
            vacuum         = true    # Remove socket stop
            enable-threads = true    # Initializes the GIL
            max-requests   = 500     # Mitigates memory leaks
            lazy-apps      = true    # Don't share database connections
            """
        ) % context
        
        nginx_file = '/etc/nginx/sites-available/%(project_name)s.conf' % context
        if server_name:
            context['server_name'] = server_name
            nginx_file = '/etc/nginx/sites-available/%(server_name)s.conf' % context
        nginx = {
            'file': nginx_file,
            'conf': nginx_conf
        }
        uwsgi = {
            'file': '/etc/uwsgi/apps-available/%(project_name)s.ini' % context,
            'conf': uwsgi_conf
        }
        
        interactive = options.get('interactive')
        for extra_context in (nginx, uwsgi):
            context.update(extra_context)
            diff = run("cat << 'EOF' | diff - %(file)s\n%(conf)s\nEOF" % context, valid_codes=(0,1,2))
            if diff.exit_code == 2:
                # File does not exist
                run("cat << 'EOF' > %(file)s\n%(conf)s\nEOF" % context, display=True)
            elif diff.exit_code == 1:
                # File is different, save the old one
                if interactive:
                    if not confirm("\n\nFile %(file)s be updated, do you like to overide "
                                   "it? (yes/no): " % context):
                        return
                run(textwrap.dedent("""\
                    cp %(file)s %(file)s.save
                    cat << 'EOF' > %(file)s
                    %(conf)s
                    EOF""") % context, display=True
                )
                self.stdout.write("\033[1;31mA new version of %(file)s has been installed.\n "
                    "The old version has been placed at %(file)s.save\033[m" % context)
        
        if server_name:
            run('ln -s /etc/nginx/sites-available/%(server_name)s.conf /etc/nginx/sites-enabled/' % context,
                valid_codes=[0,1], display=True)
        else:
            run('rm -f /etc/nginx/sites-enabled/default')
            run('ln -s /etc/nginx/sites-available/%(project_name)s.conf /etc/nginx/sites-enabled/' % context,
                valid_codes=[0,1], display=True)
        run('ln -s /etc/uwsgi/apps-available/%(project_name)s.ini /etc/uwsgi/apps-enabled/' % context,
            valid_codes=[0,1], display=True)
        
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
        run("echo '%s' > /etc/logrotate.d/nginx" % rotate, display=True)
        
        # Allow nginx to write to uwsgi socket
        run('adduser www-data %(group)s' % context, display=True)
