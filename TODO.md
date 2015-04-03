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

* LAST version of this shit http://wkhtmltopdf.org/downloads.h otml

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

* env ORCHESTRA_MASTER_SERVER='test1.orchestra.lan' ORCHESTRA_SECOND_SERVER='test2.orchestra.lan' ORCHESTRA_SLAVE_SERVER='test3.orchestra.lan' python manage.py test orchestra.apps.domains.tests.functional_tests.tests:AdminBind9BackendDomainTest --nologcapture¶



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

* SaaS model splitted into SaaSUser and SaaSSite? inherit from SaaS

* prevent @pangea.org email addresses on contacts, enforce at least one email without @pangea.org

* forms autocomplete="off", doesn't work in chrome

ln -s /proc/self/fd /dev/fd

* escape passwords and not allow ' on them !


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
* IMPORTANT make sure no order is created for mailboxes that include disk? or just don't produce lines with cost == 0 or quantity 0 ? maybe minimal quantity for billing? like 0.1 ? or minimal price? per line or per bill?

* Improve performance of admin change lists with debug toolbar and prefech_related
*  and miscellaneous.service.name == 'domini-registre' 
* DOMINI REGISTRE MIGRATION SCRIPTS

* lines too long on invoice, double lines or cut, and make margin wider
* PHP_TIMEOUT env variable in sync with fcgid idle timeout
    http://foaa.de/old-blog/2010/11/php-apache-and-fastcgi-a-comprehensive-overview/trackback/index.html#pni-top0

* payment methods icons
* use server.name | server.address on python backends, like gitlab instead of settings?
* saas change password feature (the only way of re.running a backend)

* TODO raise404, here and everywhere
* display subline links on billlines, to show that they exists.
* update service orders on a celery task? because it take alot

* billline quantity eval('10x100') instead of miningless description '(10*100)' 

# FIXME do more test, make sure billed until doesn't get uodated whhen services are billed with les metric, and don't upgrade billed_until when undoing under this circumstances
    * line 513: change threshold and one time service metric change should update last value if not billed, only record for recurring invoicing. postpay services should store the last metric for pricing period.
    * add ini, end dates on bill lines and breakup quanity into size(defaut:1) and metric
    * threshold for significative metric accountancy on services.handler
    * http://orchestra.pangea.org/admin/orders/order/6418/
    * http://orchestra.pangea.org/admin/orders/order/6495/bill_selected_orders/

* move normurlpath to orchestra.utils from websites.utils

* write down insights

* use english on services defs and so on, an translate them on render time

* websites directives get_location() and use it on last change view validation stage to compare with contents.location and also on the backend ?

* modeladmin Default filter + search isn't working, prepend filter when searching

*  IMPORTANT do all modles.py TODOs and create migrations for finished apps

* create service templates based on urlqwargs with the most basic services.

* Base price: domini propi (all domains) + extra for other domains


* prepend ORCHESTRA_ to orchestra/settings.py


* rename backends with generic names to concrete services.. eg VsFTPdTraffic, UNIXSystemUser


Translation
-----------

mkdir locale
django-admin.py makemessages -l ca
django-admin.py compilemessages -l ca

https://docs.djangoproject.com/en/1.7/topics/i18n/translation/#joining-strings-string-concat

from django.utils.translation import ugettext
from django.utils import translation
translation.activate('ca')
ugettext("Description")



* saas validate_creation generic approach, for all backends. standard output

* html code x: &times;


* periodic task to cleanup backendlogs, monitor data and metricstorage 
* create orchestrate databases.Database pk=1 -n --dry-run | --noinput --action save (default)|delete --backend name (limit to this backend) --help

* uwsgi     --max-requests=5000 \           # respawn processes after serving 5000 requests and
celery max-tasks-per-child

* generate settings.py more like django (installed_apps, middlewares, etc,,,)

* postupgradeorchestra send signals in order to hook custom stuff

* make base home for systemusers that ara homed into main account systemuser


* user force_text instead of unicode for _()

* autoscale celery workers http://docs.celeryproject.org/en/latest/userguide/workers.html#autoscaling


* Delete transaction middleware


* webapp has_website list filter



# FIXME account deletion generates a integrity error


apt-get install python3 python3-pip
cp /usr/local/lib/python2.7/dist-packages/orchestra.pth /usr/local/lib/python3.4/dist-packages/
glic3rinu's django-fluent-dashboard
* gevent is not ported to python3 :'(
* uwsgi python3


# FIXME what to do when deleting accounts? set fk null and fill a username charfield? issues, invoices.. we whant all this to go away?
* implement delete All related services
