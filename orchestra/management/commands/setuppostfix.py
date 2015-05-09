import os

from optparse import make_option

from django.core.management.base import BaseCommand

from orchestra.utils.sys import run, check_root

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--db_name', dest='db_name', default='orchestra',
                help='Specifies the database to create.'),
            make_option('--db_user', dest='db_user', default='orchestra',
                help='Specifies the database to create.'),
            make_option('--db_password', dest='db_password', default='orchestra',
                help='Specifies the database to create.'),
            make_option('--db_host', dest='db_host', default='localhost',
                help='Specifies the database to create.'),

            make_option('--vmail_username', dest='vmail_username', default='vmail',
                help='Specifies username in the operating system (default=vmail).'),
            make_option('--vmail_uid', dest='vmail_uid', default='5000',
                help='UID of user <vmail_username> (default=5000).'),
            make_option('--vmail_groupname', dest='vmail_groupname', default='vmail',
                help='Specifies the groupname in the operating system (default=vmail).'),
            make_option('--vmail_gid', dest='vmail_gid', default='5000',
                help='GID of user <vmail_username> (default=5000).'),
            make_option('--vmail_home', dest='vmail_home', default='/var/vmail',
                help='$HOME of user <vmail_username> (default=/var/vmail).'),

            make_option('--dovecot_dir', dest='dovecot_dir', default='/etc/dovecot',
                help='Dovecot root directory (default=/etc/dovecot).'),

            make_option('--postfix_dir', dest='postfix_dir', default='/etc/postfix',
                help='Postfix root directory (default=/etc/postfix).'),

            make_option('--amavis_dir', dest='amavis_dir', default='/etc/amavis',
                help='Amavis root directory (default=/etc/amavis).'),

            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleeryd process owner, which is the user how will perform tincd updates'),
            )

    option_list = BaseCommand.option_list
    help = 'Setup Postfix.'

    @check_root
    def handle(self, *args, **options):
        # Configure firmware generation
        context = {
            'db_name': options.get('db_name'),
            'db_user': options.get('db_user'),
            'db_password': options.get('db_password'),
            'db_host': options.get('db_host'),
            'vmail_username': options.get('vmail_username'),
            'vmail_uid': options.get('vmail_uid'),
            'vmail_groupname': options.get('vmail_groupname'),
            'vmail_gid': options.get('vmail_gid'),
            'vmail_home': options.get('vmail_home'),
            'dovecot_dir': options.get('dovecot_dir'),
            'postfix_dir': options.get('postfix_dir'),
            'amavis_dir': options.get('amavis_dir'),
        }

        file_name = '%(postfix_dir)s/pgsql-email2email.cf' % context
        run("#Processing %s" % file_name)
        pgsql_email2email = """user = %(db_user)s
password = %(db_password)s
hosts = %(db_host)s
dbname = %(db_name)s

query = SELECT mails_mailbox.emailname || '@' || names_domain.name as email FROM mails_mailbox INNER JOIN names_domain ON (mails_mailbox.domain_id = names_domain.id) WHERE mails_mailbox.emailname = '%%u' AND names_domain.name = '%%d'
"""
        f = open(file_name, 'w')
        f.write(pgsql_email2email % context)
        f.close()
        run("chown root:postfix %s" % file_name)
        run("chmod 640 %s" % file_name)

        file_name = '%(postfix_dir)s/pgsql-virtual-alias-maps.cf' % context
        run("#Processing %s" % file_name)
        virtual_alias_maps = """user = %(db_user)s
password = %(db_password)s
hosts = %(db_host)s
dbname = %(db_name)s

query = SELECT mails_mailalias.destination FROM mails_mailalias INNER JOIN names_domain ON (mails_mailalias.domain_id = names_domain.id) WHERE mails_mailalias.emailname = '%%u' AND names_domain.name='%%d'
"""
        f = open(file_name, 'w')
        f.write(virtual_alias_maps % context)
        f.close()
        run("chown root:postfix %s" % file_name)
        run("chmod 640 %s" % file_name)

        file_name = '%(postfix_dir)s/pgsql-virtual-mailbox-domains.cf' % context
        run("#Processing %s" % file_name)
        virtual_mailbox_domains = """user = %(db_user)s
password = %(db_password)s
hosts = %(db_host)s
dbname = %(db_name)s

query = SELECT 1 FROM names_domain WHERE names_domain.name='%%s'
"""
        f = open(file_name, 'w')
        f.write(virtual_mailbox_domains % context)
        f.close()
        run("chown root:postfix %s" % file_name)
        run("chmod 640 %s" % file_name)

        file_name = '%(postfix_dir)s/pgsql-virtual-mailbox-maps.cf' % context
        run("#Processing %s" % file_name)
        virtual_mailbox_maps = """user = %(db_user)s
password = %(db_password)s
hosts = %(db_host)s
dbname = %(db_name)s

query = SELECT 1 FROM mails_mailbox INNER JOIN names_domain ON (mails_mailbox.domain_id = names_domain.id) WHERE mails_mailbox.emailname='%%u' AND names_domain.name='%%d'
"""
        f = open(file_name, 'w')
        f.write(virtual_mailbox_maps % context)
        f.close()
        run("chown root:postfix %s" % file_name)
        run("chmod 640 %s" % file_name)

        #Dovecot
        vmail_usename = run("id -u %(vmail_username)s" % context)
        vmail_groupname = run("id -g %(vmail_groupname)s" % context)
        if vmail_groupname != context["vmail_gid"]:
            run("groupadd -g %(vmail_gid)s %(vmail_groupname)s" % context)
            run("chown -R %(vmail_username)s:%(vmail_groupname)s %(vmail_home)s" % context)
        if vmail_usename != context["vmail_uid"]:
            run("useradd -g %(vmail_groupname)s -u %(vmail_uid)s %(vmail_username)s -d %(vmail_home)s -m" % context)
            run("chmod u+w %(vmail_home)s" % context)

        run("chown -R %(vmail_username)s:%(vmail_groupname)s %(vmail_home)s" % context)
        run("chmod u+w %(vmail_home)s" % context)

        file_name = "%(dovecot_dir)s/conf.d/10-auth.conf" % context
        run("""sed -i "s/auth_mechanisms = plain$/auth_mechanisms = plain login/g" %s """ % file_name)
        run("""sed -i "s/\#\!include auth-sql.conf.ext/\!include auth-sql.conf.ext/" %s """ % file_name)

        file_name = "%(dovecot_dir)s/conf.d/auth-sql.conf.ext" % context
        run("#Processing %s" % file_name)
        auth_sql_conf_ext = """passdb {
  driver = sql
  args = %(dovecot_dir)s/dovecot-sql.conf.ext
}

userdb {
  driver = static
  args = uid=%(vmail_username)s gid=%(vmail_groupname)s home=%(vmail_home)s/%%d/%%n/Maildir allow_all_users=yes
}
"""
        f = open(file_name, 'w')
        f.write(auth_sql_conf_ext % context)
        f.close()


        file_name = "%(dovecot_dir)s/conf.d/10-mail.conf" % context
        run("#Processing %s" % file_name)
        mail_conf = """mail_location = maildir:%(vmail_home)s/%%d/%%n/Maildir
namespace inbox {
    separator = .
    inbox = yes
}
        """
        f = open(file_name, 'w')
        f.write(mail_conf % context)
        f.close()


        file_name = "%(dovecot_dir)s/conf.d/10-master.conf" % context
        run("""sed -i "s/service auth {/service auth {\\n\\tunix_listener \/var\/spool\/postfix\/private\/auth {\\n\\t\\tmode = 0660\\n\\t\\tuser = postfix\\n\\t\\tgroup = postfix\\n\\t}\\n/g" %s """ % file_name)


        file_name = "%(dovecot_dir)s/conf.d/10-ssl.conf" % context

        run("#Processing %s" % file_name)
        ssl_conf = """ssl_cert = </etc/ssl/certs/mailserver.pem
ssl_key = </etc/ssl/private/mailserver.pem"""
        f = open(file_name, 'w')
        f.write(ssl_conf)
        f.close()

        file_name = "%(dovecot_dir)s/conf.d/15-lda.conf" % context
        run("#Processing %s" % file_name)
        lda_conf ="""protocol lda {
    postmaster_address = postmaster
    mail_plugins = $mail_plugins sieve
}
"""
        f = open(file_name, 'w')
        f.write(lda_conf)
        f.close()


        file_name = "%(dovecot_dir)s/dovecot-sql.conf.ext" % context
        run("#Processing %s" % file_name)
        dovecot_sql = """driver = pgsql
connect = host=%(db_host)s dbname=%(db_name)s user=%(db_user)s password=%(db_password)s
default_pass_scheme = SSHA
password_query = \
 SELECT mails_mailbox.emailname || '@' || names_domain.name as user, mails_mailbox.shadigest as password  \\
    FROM mails_mailbox \\
        INNER JOIN names_domain ON (mails_mailbox.domain_id = names_domain.id) \\
        INNER JOIN auth_user ON (mails_mailbox.user_id = auth_user.id) \\
    WHERE mails_mailbox.emailname = '%%n' AND \\
        names_domain.name = '%%d'
        """
        f = open(file_name, 'w')
        f.write(dovecot_sql % context)
        f.close()


        run("chgrp %(vmail_groupname)s %(dovecot_dir)s/dovecot.conf" % context)
        run("chmod g+r %(dovecot_dir)s/dovecot.conf" % context)

        run("chown root:root %(dovecot_dir)s/dovecot-sql.conf.ext" % context)
        run("chmod go= %(dovecot_dir)s/dovecot-sql.conf.ext" % context)

        file_name = "%(postfix_dir)s/master.cf" % context
        grep_dovecot = run("grep dovecot %s" % file_name, valid_codes=(0,1))
        if grep_dovecot == '':
            run("#Processing %s" % file_name)
            dovecot_master="""
dovecot   unix  -       n       n       -       -       pipe
  flags=DRhu user=%(vmail_username)s:%(vmail_groupname)s argv=/usr/lib/dovecot/dovecot-lda -f ${sender} -d ${recipient}

#Amavis:
amavis unix    -       -       n       -       5     smtp
     -o smtp_data_done_timeout=1200
     -o smtp_send_xforward_command=yes
     -o smtp_tls_note_starttls_offer=no

127.0.0.1:10025 inet n    -       n       -       -     smtpd
    -o content_filter=
    -o smtpd_delay_reject=no
    -o smtpd_client_restrictions=permit_mynetworks,reject
    -o smtpd_helo_restrictions=
    -o smtpd_sender_restrictions=
    -o smtpd_recipient_restrictions=permit_mynetworks,reject
    -o smtpd_data_restrictions=reject_unauth_pipelining
    -o smtpd_end_of_data_restrictions=
    -o smtpd_restriction_classes=
    -o mynetworks=127.0.0.0/8
    -o smtpd_error_sleep_time=0
    -o smtpd_soft_error_limit=1001
    -o smtpd_hard_error_limit=1000
    -o smtpd_client_connection_count_limit=0
    -o smtpd_client_connection_rate_limit=0
    -o receive_override_options=no_header_body_checks,no_unknown_recipient_checks,no_milters
    -o local_header_rewrite_clients=
    -o smtpd_milters=
    -o local_recipient_maps=
    -o relay_recipient_maps=
              """
            f = open(file_name, 'a')
            f.write(dovecot_master % context)
            f.close()


        #Postfix
        mailname = run("cat /etc/mailname", vallid_codes=[0,1])
        hostname = run("hostname", valid_codes=[0,1])
        if mailname != hostname:
            file_name = "/etc/mailname"
            run("#Processing %s" % file_name)
            f = open(file_name, 'w')
            f.write(hostname % context)
            f.close()


        # Set the base address for all virtual mailboxes
        run("postconf -e virtual_mailbox_base=%(vmail_home)s" % context)

        # A list of all virtual domains serviced by this instance of postfix.
        run("postconf -e virtual_mailbox_domains=pgsql:%(postfix_dir)s/pgsql-virtual-mailbox-domains.cf" % context)

        # Look up the mailbox location based on the email address received.
        run("postconf -e virtual_mailbox_maps=pgsql:%(postfix_dir)s/pgsql-virtual-mailbox-maps.cf" % context)

        # Any aliases that are supported by this system
        run("postconf -e virtual_alias_maps=pgsql:%(postfix_dir)s/pgsql-virtual-alias-maps.cf" % context)

        #Dovecot:
        run("postconf -e virtual_transport=dovecot")
        run("postconf -e dovecot_destination_recipient_limit=1")
        run("postconf -e smtpd_sasl_type=dovecot")
        run("postconf -e smtpd_sasl_path=private/auth")
        run("postconf -e smtpd_sasl_auth_enable=yes")
        if os.path.isfile("/etc/ssl/certs/mailserver.pem"):
            run("postconf -e smtpd_tls_security_level=may")
            run("postconf -e smtpd_tls_auth_only=yes")
            run("postconf -e smtpd_tls_cert_file=/etc/ssl/certs/mailserver.pem")
            run("postconf -e smtpd_tls_key_file=/etc/ssl/private/mailserver.pem")

        run("""postconf -e smtpd_recipient_restrictions=permit_mynetworks,permit_sasl_authenticated,reject_invalid_hostname,reject_non_fqdn_recipient,reject_unknown_sender_domain,reject_unknown_recipient_domain,reject_unauth_destination,permit""")
        run("""postconf -e soft_bounce=no""")
        run("""postconf -e content_filter=amavis:[127.0.0.1]:10024""")

        #Amavis:
        file_name = "%(amavis_dir)s/conf.d/15-content_filter_mode" % context
        run("""sed -i "s/#@bypass_virus_checks_maps/@bypass_virus_checks_maps/g" %s""" % file_name)
        run("""sed -i 's/#   \\\\%%bypass_virus_checks, \\\@bypass_virus_checks_acl, \\\$bypass_virus_checks_re/   \\\\%%bypass_virus_checks, \\\@bypass_virus_checks_acl, \\\$bypass_virus_checks_re/g' %s""" % file_name)
        run("""sed -i 's/#   \\\\%%bypass_virus_checks/   \\\\%%bypass_virus_checks/g' %s""" % (file_name,) )
        run("""sed -i "s/#@bypass_spam_checks_maps/@bypass_spam_checks_maps/g" %s""" % file_name)
        run("""sed -i 's/#   \\\\%%bypass_spam_checks, \\\@bypass_spam_checks_acl, \\\$bypass_spam_checks_re/   \\\\%%bypass_spam_checks, \\\@bypass_spam_checks_acl, \\\$bypass_spam_checks_re/g' %s""" % file_name)

        run("adduser clamav amavis")

        run("service clamav-freshclam restart")
        run("service clamav-daemon restart")
        run("service spamassassin restart")
        run("service amavis restart")
        run("service dovecot restart")
        run("service postfix restart")
