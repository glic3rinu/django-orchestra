==== TODO ====

* scape strings before executing scripts in order to prevent exploits: django templates automatically scapes things. Most important is to ensuer that all escape ' to &quot
* Don't store passwords and other service parameters that can be changed by the services i.e. mailman, vps etc. Find an execution mechanism that trigger `change_password()`

* abort transaction on orchestration when `state == TIMEOUT` ?
* use format_html_join for orchestration email alerts

* enforce an emergency email contact and account to contact contacts about problems when mailserver is down

* add `BackendLog` retry action
* webmail identities and addresses

* use Code: https://github.com/django/django/blob/master/django/forms/forms.py#L415 for domain.refresh_serial()
* Permissions .filter_queryset()

* env vars instead of multiple settings files: https://devcenter.heroku.com/articles/config-vars ?

* Log changes from rest api (serialized objects)

* EMAIL backend operations which contain stderr messages (because under certain failures status code is still 0)

* Settings dictionary like DRF2 in order to better override large settings like WEBSITES_APPLICATIONS.etc

* backend logs with hal logo
* set_password orchestration method?

* make account_link to autoreplace account on change view.

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

* Domain backend PowerDNS Bind validation support?

* Maildir billing tests/ webdisk billing tests (avg metric)

* move icons to apps, and use appconfig to cleanup config stuff

* when using modeladmin to store shit like self.account, make sure to have a cleanslate in each request?

* jabber with mailbox accounts (dovecto mail notification)

* rename accounts register to "account", and reated api and admin references

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

* Databases.User add reverse M2M databases widget (like mailbox.addresses)

* Root owned logs on user's home ? yes

* reconsider binding webapps to systemusers (pangea multiple users wordpress-ftp, moodle-pangea, etc)
* Secondary user home in /home/secondaryuser and simlink to /home/main/webapps/app so it can have private storage?
* Grant permissions to systemusers, the problem of creating a related permission model is out of sync with the server-side. evaluate tradeoff

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

* validate systemuser.home on server-side

* webapp backend option compatibility check?

* admin systemuser home/directory, add default home and empty directory with has_shell on admin

* Resource used_list_display=True, allocated_list_displat=True, allow resources to show up on list_display

* BackendLog.updated_at (tasks that run over several minutes when finished they do not appear first on the changelist) (like celery tasks.when)

* Periodic task for cleaning old monitoring data

* Create an admin service_view with icons (like SaaS app)

* Fix ftp traffic

* Resource graph for each related object

* Rename apache logs ending on .log in order to logrotate easily

* SaaS wordpress multiple blogs per user? separate users from sites?
