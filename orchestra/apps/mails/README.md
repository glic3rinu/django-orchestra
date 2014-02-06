Emails
======

This app implements the basic functionality for managing users, mailboxes and domains of
an email server.

[Postfix Virtual Domain Hosting](https://workaround.org/ispmail/wheezy) has been used
as reference, however there is nothing in particular that stops this application to be fully
compatible with any other existing mail server, like [Sendmail](http://en.wikipedia.org/wiki/Sendmail).

So there's a command for configure it out-of-the-box:

- Dovecot
- Postfix
- Amavis for use with spamassassin

To run it:
```bash
python manage.py setuppostfix --db_name --db_user --db_password --db_host \
    --vmail_username --vmail_uid --vmail_groupname --vmail_gid --vmail_home \
    --dovecot_dir --postfix_dir --amavis_dir
```
Default values:

--db_name: orchestra

--db_user: orchestra

--db_password: orchestra

--db_host: localhost

--vmail_username: vmail

--vmail_uid: 5000

--vmail_groupname: vmail

--vmail_gid: 5000

--vmail_home: /var/vmail

--dovecot_dir: /etc/dovecot

--postfix_dir: /etc/postfix

--amavis_dir: /etc/amavis


This command is intended to configure everything from scratch. If you have configured this packages
is better to uninstall and re-install as follows:
```bash
sudo orchestra-admin uninstall_postfix
sudo orchestra-admin install_postfix
sudo python manage.py setuppostfix
```
Once finished the command we will have the fully configured mail server. Now you only need to generate the
mailboxes and aliases, and for set the password you can run the commands:

```bash
python manage.py mail-setpasswd email new_password
python manage.py mail-chpasswd  email password new_password
```

