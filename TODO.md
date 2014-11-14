TODO ====

* scape strings before executing scripts in order to prevent exploits: django templates automatically scapes things. Most important is to ensuer that all escape ' to &quot
* Don't store passwords and other service parameters that can be changed by the services i.e. mailman, vps etc. Find an execution mechanism that trigger `change_password()`

* abort transaction on orchestration when `state == TIMEOUT` ?
* use format_html_join for orchestration email alerts

* enforce an emergency email contact and account to contact contacts about problems when mailserver is down

* add `BackendLog` retry action
* webmail identities and addresses

* use Code: https://github.com/django/django/blob/master/django/forms/forms.py#L415 for domain.refresh_serial()
* Permissions .filter_queryset()

* git deploy in addition to FTP?
* env vars instead of multiple settings files: https://devcenter.heroku.com/articles/config-vars ?
* optional chroot shell?

* make sure prefetch_related() is used correctly 
Remember that, as always with QuerySets, any subsequent chained methods which imply a different database query will ignore previously cached results, and retrieve data using a fresh database query. 
* profile select_related vs prefetch_related


* Log changes from rest api (serialized objects)
* passlib; nano /usr/local/lib/python2.7/dist-packages/passlib/ext/django/utils.py SortedDict -> collections.OrderedDict
* pip install pyinotify

* Timezone awareness on monitoring system (reading server-side logs with different TZ than orchestra) maybe a settings value? (use UTC internally, timezone.localtime() when interacting with servers)

* EMAIL backend operations which contain stderr messages (because under certain failures status code is still 0)

* Settings dictionary like DRF2 in order to better override large settings like WEBSITES_APPLICATIONS.etc

* DOCUMENT: orchestration.middleware: we need to know when an operation starts and ends in order to perform bulk server updates and also to wait for related objects to be saved (base object is saved first and then related)
            orders.signales: we perform changes right away because data model state can change under monitoring and other periodik task, and we should keep orders consistency under any situation.
                             dependency collector with max_recursion that matches the number of dots on service.match and service.metric


* backend logs with hal logo
* Use logs for storing monitored values
* set_password orchestration method?


* make account_link to autoreplace account on change view.

* LAST version of this shit http://wkhtmltopdf.org/downloads.html

* translations
        from django.utils import translation
        with translation.override('en'):
* Plurals!

* help_text on readonly_fields specialy Bill.state. (eg. A bill is in OPEN state when bla bla )

* underescore *every* private function

* create log file at /var/log/orchestra.log and rotate

* order.register_at
    @property
    def register_on(self):
        return order.register_at.date()

* mail backend related_models = ('resources__content_type') ??

* Domain backend PowerDNS Bind validation support?

* Maildir billing tests/ webdisk billing tests (avg metric)

* move icons to apps, and use appconfig to cleanup config stuff

* when using modeladmin to store shit like self.account, make sure to have a cleanslate in each request

* jabber with mailbox accounts (dovecto mail notification)

* rename accounts register to manager register or accounttools, accountutils

* take a look icons from ajenti ;)

* Disable services is_active should be computed on the fly in order to distinguish account.is_active from service.is_active when reactivation.
    * Perhaps it is time to create a ServiceModel ?

* prevent deletion of main user by the user itself

* AccountAdminMixin auto adds 'account__name' on searchfields and handle account_link on fieldsets

* Separate panel from server passwords?  Store passwords on panel? set_password special backend operation?

* What fields we really need on contacts? name email phone and what more?

* Redirect junk emails and delete every 30 days?

* DOC: Complitely decouples scripts execution, billing, service definition

* delete main user -> delete account or prevent delete main user

* Ansible orchestration *method* (methods.py)
* multiple domains creation; line separated domains
* Move MU webapps to SaaS?

* offer to create mailbox on account creation
* init.d celery scripts
    -# Required-Start:    $network $local_fs $remote_fs postgresql celeryd
    -# Required-Stop:     $network $local_fs $remote_fs postgresql celeryd

* for list virtual_domains cleaning up we need to know the old domain name when a list changes its address domain, but this is not possible with the current design.
* regenerate virtual_domains every time (configure a separate file for orchestra on postfix)
* update_fields=[] doesn't trigger post save!

* Backend optimization
    * fields = ()
    * ignore_fields = ()
    * based on a merge set of save(update_fields)

* textwrap.dedent( \\)
* parmiko write to a channel instead of transfering files?  http://sysadmin.circularvale.com/programming/paramiko-channel-hangs/


* proforma without billing contact?

* env ORCHESTRA_MASTER_SERVER='test1.orchestra.lan' ORCHESTRA_SECOND_SERVER='test2.orchestra.lan' ORCHESTRA_SLAVE_SERVER='test3.orchestra.lan' python manage.py test orchestra.apps.domains.tests.functional_tests.tests:AdminBind9BackendDomainTest

* Pangea modifications: domain registered/non-registered list_display and field with register link: inconsistent, what happen to related objects with a domain that is converted to register-only?

* ForeignKey.swappable
* Field.editable
* ManyToManyField.symmetrical = False (user group)

* REST PERMISSIONS

* caching based on "def text2int(textnum, numwords={}):"

* multiple files monitoring

* Split plans into a separate app (plans and rates / services ) interface ?

* sync() ServiceController method that synchronizes orchestra and servers (delete or import)

* consider removing mailbox support on forward (user@pangea.org instead)

* remove ordering in account admin and others admininlines

* Databases.User add reverse M2M databases widget (like mailbox.addresses)

* Change (correct) permissions periodically on the web server, to ensure security ?

* Root owned logs on user's home ? yes

* reconsider binding webapps to systemusers (pangea multiple users wordpress-ftp, moodle-pangea, etc)
* Secondary user home in /home/secondaryuser and simlink to /home/main/webapps/app so it can have private storage?
* Grant permissions to systemusers, the problem of creating a related permission model is out of sync with the server-side. evaluate tradeoff

* Secondaryusers home should be under mainuser home. i.e. /home/mainuser/webapps/seconduser_webapp/
* Make one dedicated CGI user for each account only for CGI execution (fpm/fcgid). Different from the files owner, and without W permissions, so attackers can not inject backdors and malware.
* In most cases we can prevent the creation of files for the CGI users, preventing attackers to upload and executing PHPShells.
* Make main systemuser able to write/read everything on its home, including stuff created by the CGI user and secondary users
* Prevent users from accessing other users home while at the same time allow access Apache/fcgid/fpm and secondary users (x)

* public_html/webapps directory with root owner and permissions

* resource min max allocation with validation

* mailman needs both aliases when address_name is provided (default messages and bounces and all)

* domain validation parse named-checzone output to assign errors to fields

* Directory Protection on webapp and use webapp path as base path (validate)
* User [Group] webapp/website option (validation) which overrides default mainsystemuser

* validate systemuser.home

* webapp backend option compatibility check?


* ServiceBackend.validate() : used for server paths validation
* ServiceBackend.grant_access() : used for granting access
* bottom line: allow arbitrary backend methods (underscore method names that are not to be executed?)
* HowTo?? Signals ? what?
