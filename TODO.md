==== TODO ====
* use format_html_join for orchestration email alerts

* enforce an emergency email contact and account to contact contacts about problems when mailserver is down

* add `BackendLog` retry action

* webmail identities and addresses

* Permissions .filter_queryset()

* env vars instead of multiple settings files: https://devcenter.heroku.com/articles/config-vars ?

* backend logs with hal logo

* LAST version of this shit http://wkhtmltopdf.org/downloads.h otml

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

* AccountAdminMixin auto adds 'account__name' on searchfields

* What fields we really need on contacts? name email phone and what more?

* Redirect junk emails and delete every 30 days?

* DOC: Complitely decouples scripts execution, billing, service definition

* init.d celery scripts
    -# Required-Start:    $network $local_fs $remote_fs postgresql celeryd
    -# Required-Stop:     $network $local_fs $remote_fs postgresql celeryd

* regenerate virtual_domains every time (configure a separate file for orchestra on postfix)

* Backend optimization
    * fields = ()
    * ignore_fields = ()
    * based on a merge set of save(update_fields)

* proforma without billing contact?

* print open invoices as proforma?

* env ORCHESTRA_MASTER_SERVER='test1.orchestra.lan' ORCHESTRA_SECOND_SERVER='test2.orchestra.lan' ORCHESTRA_SLAVE_SERVER='test3.orchestra.lan' python manage.py test orchestra.apps.domains.tests.functional_tests.tests:AdminBind9BackendDomainTest --nologcapture

* ForeignKey.swappable
* Field.editable
* ManyToManyField.symmetrical = False (user group)

* REST PERMISSIONS

* caching based on "def text2int(textnum, numwords={}):"

* sync() ServiceController method that synchronizes orchestra and servers (delete or import)

* consider removing mailbox support on forward (user@pangea.org instead)

* Databases.User add reverse M2M databases widget (like mailbox.addresses)

* Grant permissions to systemusers

* Make one dedicated CGI user for each account only for CGI execution (fpm/fcgid). Different from the files owner, and without W permissions, so attackers can not inject backdors and malware.

* resource min max allocation with validation

* domain validation parse named-checzone output to assign errors to fields

* Directory Protection on webapp and use webapp path as base path (validate)

* validate systemuser.home on server-side

* webapp backend option compatibility check? raise exception, missconfigured error

* admin systemuser home/directory, add default home and empty directory with has_shell on admin

* Resource used_list_display=True, allocated_list_displat=True, allow resources to show up on list_display

* BackendLog.updated_at (tasks that run over several minutes when finished they do not appear first on the changelist) (like celery tasks.when)

* Periodic task for cleaning old monitoring data

* Create an admin service_view with icons (like SaaS app)

* Resource graph for each related object

* SaaS model splitted into SaaSUser and SaaSSite? inherit from SaaS, proxy model?

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

* user provided crons

* ```<?php
$moodle_host = $SERVER[‘HTTP_HOST’];
require_once(‘/etc/moodles/’.$moodle_host.‘config.php’);``` moodle/drupla/php-list multi-tenancy

* make account available on all admin forms

# WPMU blog traffic

* more robust backend error handling, continue executing but exit code > 0 if failure: failing_cmd || exit_code=1 and don't forget to call super.commit()!!

* website directives uniquenes validation on serializers

+ is_Active custom filter with support for instance.account.is_Active annotate with F() needed (django 1.8)

# delete apache logs and php logs

* document service help things: discount/refound/compensation effect and metric table
* Document metric interpretation help_text
* document plugin serialization, data_serializer?

# bill line managemente, remove, undo (only when possible), move, copy, paste
    * budgets: no undo feature

* Autocomplete admin fields like <site_name>.phplist... with js

* allow empty metric pack for default rates? changes on rating algo
# don't produce lines with cost == 0 or quantity 0 ? maybe minimal quantity for billing? like 0.1 ? or minimal price? per line or per bill?

# lines too long on invoice, double lines or cut, and make margin wider

* payment methods icons
* use server.name | server.address on python backends, like gitlab instead of settings?

* TODO raise404, here and everywhere
* update service orders on a celery task? because it take alot

# FIXME do more test, make sure billed until doesn't get uodated whhen services are billed with les metric, and don't upgrade billed_until when undoing under this circumstances
    * line 513: change threshold and one time service metric change should update last value if not billed, only record for recurring invoicing. postpay services should store the last metric for pricing period.
    * add ini, end dates on bill lines and breakup quanity into size(defaut:1) and metric
    * threshold for significative metric accountancy on services.handler
    * http://orchestra.pangea.org/admin/orders/order/6418/
    * http://orchestra.pangea.org/admin/orders/order/6495/bill_selected_orders/

* move normurlpath to orchestra.utils from websites.utils

* write down insights

* websites directives get_location() and use it on last change view validation stage to compare with contents.location and also on the backend ?

* modeladmin Default filter + search isn't working, prepend filter when searching

* create service help templates based on urlqwargs with the most basic services.

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

* html code x: &times; for bill line verbose quantity

* periodic task to cleanup backendlogs, monitor data and metricstorage 
* create orchestrate databases.Database pk=1 -n --dry-run | --noinput --action save (default)|delete --backend name (limit to this backend) --help

* uwsgi     --max-requests=5000 \           # respawn processes after serving 5000 requests and
celery max-tasks-per-child

* generate settings.py more like django (installed_apps, middlewares, etc,,,)

* postupgradeorchestra send signals in order to hook custom stuff

* autoscale celery workers http://docs.celeryproject.org/en/latest/userguide/workers.html#autoscaling


glic3rinu's django-fluent-dashboard
* gevent is not ported to python3 :'(

# FIXME account deletion generates an integrity error
https://code.djangoproject.com/ticket/24576
# FIXME what to do when deleting accounts? set fk null and fill a username charfield? issues, invoices.. we whant all this to go away?
* implement delete All related services

# FIXME address name change does not remove old one :P, readonly or perhaps we can regenerate all addresses using backend.prepare()?

* read https://docs.djangoproject.com/en/dev/releases/1.8/ and fix deprecation warnings

* create nice fieldsets for SaaS, WebApp types and services, and helptexts too!

* replace make_option in management commands

# FIXME model contact info and account info (email, name, etc) correctly/unredundant/dry

* Use the new django.contrib.admin.RelatedOnlyFieldListFilter in ModelAdmin.list_filter to limit the list_filter choices to foreign objects which are attached to those from the ModelAdmin.
+ Query Expressions, Conditional Expressions, and Database Functions¶
* forms: You can now pass a callable that returns an iterable of choices when instantiating a ChoiceField.

* move all tests to django-orchestra/tests
* *natural keys: those fields that uniquely identify a service, list.name, website.name, webapp.name+account, make sure rest api can not edit thos things

# migrations accounts, bill, orders, auth -> migrate the rest (contacts lambda error)


* MultiCHoiceField proper serialization

* UNIFY PHP FPM settings name
# virtualhost name: name-account?
* add a delay to changes on the webserver apache to no overwelm it with backend executions?
* replace unique_name by natural_key?
* do not require contact or create default
* send signals for backend triggers
* force ignore slack billing period overridig when billing
* fpm reload starts new pools?
* rename resource.monitors to resource.backends ?
* abstract model classes that enabling overriding, and ORCHESTRA_DATABASE_MODEL settings + orchestra.get_database_model() instead of explicitly importing from orchestra.contrib.databases.models import Database.. (Admin and REST API are fucked then?)

# billing order list filter detect metrics that are greater from those of billing_date
# Ignore superusers & co on billing: list filter doesn't work nor ignore detection
# bill.totals make it 100% computed?
* joomla: wget https://github.com/joomla/joomla-cms/releases/download/3.4.1/Joomla_3.4.1-Stable-Full_Package.tar.gz -O - | tar xvfz -


# bill confirmation: show total
# Amend lines???
# orders currency setting

# Determine the difference between data serializer used for validation and used for the rest API!
# Make PluginApiView that fills metadata and other stuff like modeladmin plugin support

# custom validation for settings
# TODO orchestra related services code reload: celery/uwsgi reloading find aonther way without root and implement reload
# insert settings on dashboard dynamically

# convert all complex settings to string
# @ something database names
# password validation cracklib on change password form=?????
# reset setting buton 

# periodic cleaning of spam mailboxes

# admin edit relevant djanog settings
# django SITE_NAME vs ORCHESTRA_SITE_NAME ?


Replace celery by a custom solution?
    # TODO create decorator wrapper that abstract the task away from the backen (cron/celery)
    # TODO crontab model localhost/autoadded attribute
    * No more jumbo dependencies and wierd bugs
    1) Periodic Monitoring:
        * runtask management command + crontab scheduling or high performance beat crontab (not loading bloated django system)
    2) Single time shot:
        sys.run("python3 manage.py runtas 'task' args")
    3) Emails:
        Custom backend that distinguishes between priority and bulk mail
            *priority: custom Thread backend
            *bulk: wrapper arround django-mailer to avoid loading django system

python3 -mvenv env-django-orchestra
source env-django-orchestra/bin/activate
pip3 install django-orchestra==dev --allow-external django-orchestra --allow-unverified django-orchestra
pip3 install -r https://raw.githubusercontent.com/glic3rinu/django-orchestra/master/requirements.txt

# TODO make them optional
sudo apt-get install python3.4-dev libxml2-dev libxslt1-dev libcrack2-dev
wget -O - https://raw.githubusercontent.com/glic3rinu/django-orchestra/master/requirements.txt | xargs pip3 install
orchestra-admin startproject panel
python3 panel/manage.py migrate accounts
python3 panel/manage.py migrate
python3 panel/manage.py runserver

http://localhost:8000/admin/

setupcrontab


Collecting lxml==3.3.5 (from -r re (line 22))
  Downloading lxml-3.3.5.tar.gz (3.5MB)
    100% |################################| 3.5MB 60kB/s 
    Building lxml version 3.3.5.
    Building without Cython.
    ERROR: b'/bin/sh: 1: xslt-config: not found\n'
    ** make sure the development packages of libxml2 and libxslt are installed **
    Using build configuration of libxslt
    /usr/lib/python3.4/distutils/dist.py:260: UserWarning: Unknown distribution option: 'bugtrack_url'
      warnings.warn(msg)


# Setupcron
# uwsgi enable threads
# register signals in app ready()
# database_ready(): connect to the database or inspect django connection

# move Setting to contrib app __init__
# cracklib vs crack
# remove system dependencies
# deprecate install_dependnecies in favour of only requirements.txt
# import module and sed
# if setting.value == default. remove
# cron backend: os.cron or uwsgi.cron
# reload generic admin view ?redirect=http...
# inspecting django db connection for asserting db readines?
# wake up django mailer on send_mail

# project settings modified copy of django's default project settings
