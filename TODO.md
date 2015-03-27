==== TODO ====

* scape strings before executing scripts in order to prevent exploits: django templates automatically scapes things. Most important is to ensuer that all escape ' to &quot
* Don't store passwords and other service parameters that can be changed by the services i.e. mailman, vps etc. Find an execution mechanism that trigger `change_password()`

* abort transaction on orchestration when `state == TIMEOUT` ?
* use format_html_join for orchestration email alerts

* enforce an emergency email contact and account to contact contacts about problems when mailserver is down

* add `BackendLog` retry action
* webmail identities and addresses

* Permissions .filter_queryset()

* env vars instead of multiple settings files: https://devcenter.heroku.com/articles/config-vars ?

* Log changes from rest api (serialized objects)


* backend logs with hal logo

* LAST version of this shit http://wkhtmltopdf.org/downloads.html

* translations
    from django.utils import translation
    with translation.override('en'):

* help_text on readonly_fields specialy Bill.state. (eg. A bill is in OPEN state when bla bla )

* create log file at /var/log/orchestra.log and rotate

* order.register_at
    @property
    def register_on(self):
        return order.register_at.date()

* mail backend related_models = ('resources__content_type') ??

* Maildir billing tests/ webdisk billing tests (avg metric)


* when using modeladmin to store shit like self.account, make sure to have a cleanslate in each request? no, better reuse the last one

* jabber with mailbox accounts (dovecot mail notification)

* rename accounts register to "account", and reated api and admin references

* prevent deletion of main user by the user itself

* AccountAdminMixin auto adds 'account__name' on searchfields

* Separate panel from server passwords?  Store passwords on panel? set_password special backend operation?

* What fields we really need on contacts? name email phone and what more?

* Redirect junk emails and delete every 30 days?

* DOC: Complitely decouples scripts execution, billing, service definition

* delete main user -> delete account or prevent delete main user


* multiple domains creation; line separated domains


* init.d celery scripts
    -# Required-Start:    $network $local_fs $remote_fs postgresql celeryd
    -# Required-Stop:     $network $local_fs $remote_fs postgresql celeryd


* regenerate virtual_domains every time (configure a separate file for orchestra on postfix)
* update_fields=[] doesn't trigger post save!

* Backend optimization
    * fields = ()
    * ignore_fields = ()
    * based on a merge set of save(update_fields)

* parmiko write to a channel instead of transfering files?  http://sysadmin.circularvale.com/programming/paramiko-channel-hangs/

* proforma without billing contact?

* print open invoices as proforma?

* env ORCHESTRA_MASTER_SERVER='test1.orchestra.lan' ORCHESTRA_SECOND_SERVER='test2.orchestra.lan' ORCHESTRA_SLAVE_SERVER='test3.orchestra.lan' python manage.py test orchestra.apps.domains.tests.functional_tests.tests:AdminBind9BackendDomainTest


* ForeignKey.swappable
* Field.editable
* ManyToManyField.symmetrical = False (user group)

* REST PERMISSIONS

* caching based on "def text2int(textnum, numwords={}):"

* multiple files monitoring

* sync() ServiceController method that synchronizes orchestra and servers (delete or import)

* consider removing mailbox support on forward (user@pangea.org instead)

* Databases.User add reverse M2M databases widget (like mailbox.addresses)

* reconsider binding webapps to systemusers (pangea multiple users wordpress-ftp, moodle-pangea, etc)
* Secondary user home in /home/secondaryuser and simlink to /home/main/webapps/app so it can have private storage?
* Grant permissions to systemusers, the problem of creating a related permission model is out of sync with the server-side. evaluate tradeoff

* Make one dedicated CGI user for each account only for CGI execution (fpm/fcgid). Different from the files owner, and without W permissions, so attackers can not inject backdors and malware.
* In most cases we can prevent the creation of files for the CGI users, preventing attackers to upload and executing PHPShells.
* Make main systemuser able to write/read everything on its home, including stuff created by the CGI user and secondary users
* Prevent users from accessing other users home while at the same time allow access Apache/fcgid/fpm and secondary users (x)

* resource min max allocation with validation

* mailman needs both aliases when address_name is provided (default messages and bounces and all)

* domain validation parse named-checzone output to assign errors to fields

* Directory Protection on webapp and use webapp path as base path (validate)
* User [Group] webapp/website option (validation) which overrides default mainsystemuser

* validate systemuser.home on server-side

* webapp backend option compatibility check?

* admin systemuser home/directory, add default home and empty directory with has_shell on admin

* Resource used_list_display=True, allocated_list_displat=True, allow resources to show up on list_display

* BackendLog.updated_at (tasks that run over several minutes when finished they do not appear first on the changelist) (like celery tasks.when)

* Periodic task for cleaning old monitoring data

* Create an admin service_view with icons (like SaaS app)

* Resource graph for each related object

* Service.account change and orders consistency

* SaaS model splitted into SaaSUser and SaaSSite? inherit from SaaS

* prevent @pangea.org email addresses on contacts, enforce at least one email without @pangea.org

* forms autocomplete="off", doesn't work in chrome


ln -s /proc/self/fd /dev/fd



POST INSTALL
------------

* Generate a password-less ssh key, and copy it to the servers you want to orchestrate.
ssh-keygen
ssh-copy-id root@<server-address>

Php binaries should have this format: /usr/bin/php5.2-cgi



* logs on panel/logs/ ? mkdir ~webapps, backend post save signal? 
* transaction fault tolerant on backend.execute()
* <IfModule security2_module> and other IfModule on backend SecRule


* Orchestra global search box on the page head, based https://github.com/django/django/blob/master/django/contrib/admin/options.py#L866 and iterating over all registered services and inspectin its admin.search_fields


* contain error on plugin missing key (plugin dissabled): NOP, fail hard is better than silently, perhaps fail at starttime? apploading machinary

* contact.alternative_phone on a phone.tooltip, email:to

* better validate options and directives (url locations, filesystem paths, etc..)

* make sure that you understand the risks

* full support for deactivation of services/accounts
    * Display admin.is_active (disabled account special icon and order by support)

* lock resource monitoring
* -EXecCGI in common CMS upload locations /wp-upload/upload/uploads
* cgi user / pervent shell access

* prevent stderr when users exists on backend i.e. mysql user create

* disable anonymized list options (mailman)

* tags = GenericRelation(TaggedItem, related_query_name='bookmarks')

* make home for all systemusers (/home/username) and fix monitors

* user provided crons

* ```<?php
$moodle_host = $SERVER[‘HTTP_HOST’];
require_once(‘/etc/moodles/’.$moodle_host.‘config.php’);``` moodle/drupla/php-list multi-tenancy

* make account available on all admin forms

* WPMU blog traffic

* normurlpath '' return '/'

* more robust backend error handling, continue executing but exit code > 0 if failure: failing_cmd || exit_code=1 and don't forget to call super.commit()!!

* website directives uniquenes validation on serializers

+ is_Active custom filter with support for instance.account.is_Active annotate with F() needed (django 1.8)

* delete apache logs and php logs

* document service help things: discount/refound/compensation effect and metric table
* Document metric interpretation help_text
* document plugin serialization, data_serializer?

* bill line managemente, remove, undo (only when possible), move, copy, paste
    * budgets: no undo feature

* Autocomplete admin fields like <site_name>.phplist... with js
* autoexpand mailbox.filter according to filtering options

* allow empty metric pack for default rates? changes on rating algo
* rates plan verbose name!"!
* IMPORTANT make sure no order is created for mailboxes that include disk? or just don't produce lines with cost == 0
* IMPORTANT maildis updae and metric storage ?? threshold ? or what?

* Improve performance of admin change lists with debug toolbar and prefech_related
*  and miscellaneous.service.name == 'domini-registre' 
* DOMINI REGISTRE MIGRATION SCRIPTS

* detect subdomains accounts correctly with subdomains: i.e. www.marcay.pangea.org
* lines too long on invoice, double lines or cut
