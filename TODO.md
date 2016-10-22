==== TODO ====
* use format_html_join for orchestration email alerts

* enforce an emergency email contact and account to contact contacts about problems when mailserver is down

* add `BackendLog` retry action

* webmail identities and addresses

* Permissions .filter_queryset()

* env vars instead of multiple settings files: https://devcenter.heroku.com/articles/config-vars ?

* backend logs with hal logo

* help_text on readonly_fields specialy Bill.state. (eg. A bill is in OPEN state when bla bla )

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

* env ORCHESTRA_MASTER_SERVER='test1.orchestra.lan' ORCHESTRA_SECOND_SERVER='test2.orchestra.lan' ORCHESTRA_SLAVE_SERVER='test3.orchestra.lan' python3 manage.py test orchestra.contrib.domains.tests.functional_tests.tests:AdminBind9BackendDomainTest --nologcapture --keepdb

* ForeignKey.swappable

* REST PERMISSIONS

* Databases.User add reverse M2M databases widget (like mailbox.addresses)

* Make one dedicated CGI user for each account only for CGI execution (fpm/fcgid). Different from the files owner, and without W permissions, so attackers can not inject backdors and malware.

* resource min max allocation with validation

* domain validation parse named-checzone output to assign errors to fields

* Directory Protection on webapp and use webapp path as base path (validate)

* webapp backend option compatibility check? raise exception, missconfigured error

* Resource used_list_display=True, allocated_list_displat=True, allow resources to show up on list_display

* BackendLog.updated_at (tasks that run over several minutes when finished they do not appear first on the changelist) (like celery tasks.when)

* Create an admin service_view with icons (like SaaS app)

* prevent @pangea.org email addresses on contacts, enforce at least one email without @pangea.org

ln -s /proc/self/fd /dev/fd


POST INSTALL
------------

* Generate a password-less ssh key, and copy it to the servers you want to orchestrate.
ssh-keygen
ssh-copy-id root@<server-address>

Php binaries should have this format: /usr/bin/php5.2-cgi


* logs on panel/logs/ ? mkdir ~webapps, backend post save signal? 
* <IfModule security2_module> and other IfModule on backend SecRule

# Orchestra global search box on the page head, based https://github.com/django/django/blob/master/django/contrib/admin/options.py#L866 and iterating over all registered services and inspectin its admin.search_fields

* contain error on plugin missing key (plugin dissabled): NOP, fail hard is better than silently, perhaps fail at starttime? apploading machinary

* contact.alternative_phone on a phone.tooltip, email:to

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

* more robust backend error handling, continue executing but exit code > 0 if failure: failing_cmd || exit_code=1 and don't forget to call super.commit()!!

* website directives uniquenes validation on serializers

+ is_Active custom filter with support for instance.account.is_Active annotate with F() needed (django 1.8)

* document service help things: discount/refound/compensation effect and metric table
* Document metric interpretation help_text
* document plugin serialization, data_serializer?
* Document strong input validation

# bill line managemente, remove, undo (only when possible), move, copy, paste
    * budgets: no undo feature

* Autocomplete admin fields like <site_name>.phplist... with js

* allow empty metric pack for default rates? changes on rating algo

* payment methods icons
* use server.name | server.address on python backends, like gitlab instead of settings?

* TODO raise404, here and everywhere
* update service orders on a celery task? because it take alot

# FIXME do more test, make sure billed until doesn't get uodated whhen services are billed with les metric, and don't upgrade billed_until when undoing under this circumstances
#    * line 513: change threshold and one time service metric change should update last value if not billed, only record for recurring invoicing. postpay services should store the last metric for pricing period.
#    * add ini, end dates on bill lines and breakup quanity into size(defaut:1) and metric
#    * threshold for significative metric accountancy on services.handler
#    * http://orchestra.pangea.org/admin/orders/order/6418/

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

# create orchestrate databases.Database pk=1 -n --dry-run | --noinput --action save (default)|delete --backend name (limit to this backend) --help

* postupgradeorchestra send signals in order to hook custom stuff

* gevent is not ported to python3 :'(

# FIXME account deletion generates an integrity error
https://code.djangoproject.com/ticket/24576
# FIXME what to do when deleting accounts? set fk null and fill a username charfield? issues, invoices.. we whant all this to go away?
* implement delete All related services

* read https://docs.djangoproject.com/en/dev/releases/1.8/ and fix deprecation warnings

* create nice fieldsets for SaaS, WebApp types and services, and helptexts too!

* replace make_option in management commands

# FIXME model contact info and account info (email, name, etc) correctly/unredundant/dry

* Use the new django.contrib.admin.RelatedOnlyFieldListFilter in ModelAdmin.list_filter to limit the list_filter choices to foreign objects which are attached to those from the ModelAdmin.
+ Query Expressions, Conditional Expressions, and Database Functions¶
* forms: You can now pass a callable that returns an iterable of choices when instantiating a ChoiceField.

* move all tests to django-orchestra/tests
* *natural keys: those fields that uniquely identify a service, list.name, website.name, webapp.name+account, make sure rest api can not edit thos things

* MultiCHoiceField proper serialization

* replace unique_name by natural_key?
* do not require contact or create default
* abstract model classes that enabling overriding, and ORCHESTRA_DATABASE_MODEL settings + orchestra.get_database_model() instead of explicitly importing from orchestra.contrib.databases.models import Database.. (Admin and REST API are fucked then?)

# billing order list filter detect metrics that are greater from those of billing_date
# Ignore superusers & co on billing: list filter doesn't work nor ignore detection
# bill.totals make it 100% computed?
* joomla: wget https://github.com/joomla/joomla-cms/releases/download/3.4.1/Joomla_3.4.1-Stable-Full_Package.tar.gz -O - | tar xvfz -

# Amend lines???
# orders currency setting

# Determine the difference between data serializer used for validation and used for the rest API!
# Make PluginApiView that fills metadata and other stuff like modeladmin plugin support

# reset setting button 

# admin edit relevant djanog settings
# django SITE_NAME vs ORCHESTRA_SITE_NAME ?


# TASKS_ENABLE_UWSGI_CRON_BEAT (default) for production + system check --deploy
    if 'wsgi' in sys.argv and settings.TASKS_ENABLE_UWSGI_CRON_BEAT:
        import uwsgi
        def uwsgi_beat(signum):
            print "It's 5 o'clock of the first day of the month."
        uwsgi.register_signal(99, '', uwsgi_beat)
        uwsgi.add_timer(99, 60)
# TASK_BEAT_BACKEND = ('cron', 'celerybeat', 'uwsgi')
# Ship orchestra production-ready (no DEBUG etc)

# reload generic admin view ?redirect=http...
# inspecting django db connection for asserting db readines? or performing a query
* wake up django mailer on send_mail

        from orchestra.contrib.tasks import task
        import time, sys
        @task(name='rata')
        def counter(num, log):
            for i in range(1, num):
                with open(log, 'a') as handler:
                    handler.write(str(i))
                sys.stderr.write('hola\n')
                time.sleep(1)
        counter.apply_async(10, '/tmp/kakas')

* Provide some fixtures with mocked data


TODO http://wiki2.dovecot.org/HowTo/SimpleVirtualInstall
TODO http://wiki2.dovecot.org/HowTo/VirtualUserFlatFilesPostfix
TODO mount the filesystem with "nosuid" option

* uwse uwsgi cron: decorator or config cron = 59 2 -1 -1 -1 %(virtualenv)/bin/python manage.py runmyfunnytask

# mailboxes.address settings multiple local domains, not only one?
# backend.context = self.get_context() or save(obj, context=None) ?? more like form.cleaned_data

# smtplib.SMTPConnectError: (421, b'4.7.0 mail.pangea.org Error: too many connections from 77.246.181.209')

# rename virtual_maps to virtual_alias_maps and remove virtual_alias_domains ?
# virtdomains file is not ideal, prevent user provided fake/error domains there! and make sure to chekc if this file is required!

# Deprecate restart/start/stop services (do touch wsgi.py and fuck celery)
orchestra-beat support for uwsgi cron

make django admin taskstate uncollapse fucking traceback, ( if exists ?)

# form for custom message on admin save "comment & save"?

# backend.context and backned.instance provided when an action is called? like forms.cleaned_data: do it on manager.generation(backend.context = backend.get_context()) or in backend.__getattr__ ? also backend.head,tail,content switching on manager.generate()?

resorce monitoring more efficient, less mem an better queries for calc current data

# bill this https://orchestra.pangea.org/admin/orders/order/8236/ should be already billed, <= vs <
# Convert rating method from function to PluginClass

# autoresponses on mailboxes, not addresses or remove them

# force save and continue on routes (and others?)
# gevent for python3
apt-get install cython3
export CYTHON='cython3'
pip3 install https://github.com/fantix/gevent/archive/master.zip


# SIgnal handler for notify workers to reload stuff, like resource sync: https://docs.python.org/2/library/signal.html

# BUG Delete related services also deletes account!

# get_related service__rates__isnull=TRue is that correct?

# uwsgi hot reload? http://uwsgi-docs.readthedocs.org/en/latest/articles/TheArtOfGracefulReloading.html

# change mailer.message.priority by, queue/sent inmediatelly or rename critical to noq


method(
    arg, arg, arg)


Bash/Python/PHPController

# services.handler as generator in order to save memory? not swell like a balloon

import uwsgi
from uwsgidecorators import timer
from django.utils import autoreload

@timer(3)
def change_code_gracefull_reload(sig):
    if autoreload.code_changed():
        uwsgi.reload()
# using kill to send the signal
kill -HUP `cat /tmp/project-master.pid`
# or the convenience option --reload
uwsgi --reload /tmp/project-master.pid
# or if uwsgi was started with touch-reload=/tmp/somefile
touch /tmp/somefile

# Serializers.validation migration to DRF3: grep -r 'attrs, source' *|grep -v '~'
serailzer self.instance on create.

* check certificate: websites directive ssl + domains search on miscellaneous

# billing invoice link on related invoices not overflow nginx GET vars

* backendLog store method and language... and use it for display_script with correct lexer

@register.filter
def comma(value):
    value = str(value)
    if '.' in value:
        left, right = str(value).split('.')
        return ','.join((left, right))
    return value


# payment/bill report allow to change template using a setting variable
# Payment transaction stats, graphs over time

reporter.stories_filed = F('stories_filed') + 1
reporter.save()
In order to access the new value that has been saved in this way, the object will need to be reloaded:
https://docs.djangoproject.com/en/dev/ref/models/conditional-expressions/
Greatest
Colaesce('total', 'computed_total')
Case

# SQL case on payment transaction state ? case when trans.amount > 

# Resource inline links point to custom changelist view that preserve state (breadcrumbs, title, etc) rather than generic changeview with queryarg filtering

# ORDER diff Pending vs ALL

# DELETING RESOURCE RELATED OBJECT SHOULD NOT delete related monitor data for traffic accountancy

# round decimals on every billing operation

# use "su $user --shell /bin/bash" on backends for security : MKDIR -p...

# model.field.flatchoices

* This is beta software, please test thoroughly before putting into production and report back any issues.

# messages SMTP errors: temporary->deferre else Failed

# Don't enforce one contact per account? remove account.email in favour of contacts?

# Mailer: mark as sent
# Mailer: download attachments

# Enable/disable ignore period orders list filter


# Modsecurity rules template by cms (wordpress, joomla, dokuwiki (973337 973338 973347 958057), ...



deploy --dev
deploy.sh  and deploy-dev.sh autoupgrade

short URLS: https://github.com/rsvp/gitio

link backend help text variables to settings/#var_name

mkhomedir_helper or create ssh homes with bash.rc and such

# warnings if some plugins are disabled, like make routes red
# replace show emails by https://docs.python.org/3/library/email.contentmanager.html#module-email.contentmanager



# setupforbiddendomains --url alexa -n 5000


* remove welcome box on dashboard?

# account contacts inline, show provided fields and ignore the rest? 
# email usage -webkit-column-count:3;-moz-column-count:3;column-count:3;


# validate_user on saas.wordpress to detect if username already exists before attempting to create a blog


# webapps don't override owner and permissions on every save(), just on create
# webapps php fpm allow pool config to be overriden. template + pool inheriting template?
# get_context signal to overridaconfiguration? best practice: all context on get_context, ever use other context. template rendering as backend generator: proof of concept


# if not database_ready(): schedule a retry in 60 seconds, otherwise resources and other dynamic content gets fucked, maybe attach some 'signal' when first query goes trough
    with database_ready:
        shit_happend, otherwise schedule for first query
# Entry.objects.filter()[:1].first() (LIMIT 1)


# Reverse lOgHistory order by date (lastest first)

* setuppostgres use porject_name for db name and user instead of orchestra

# POSTFIX web traffic monitor '": uid=" from=<%(user)s>'

# Automatically re-run backends until success? only timedout executions?
# TODO save serialized versions ob backendoperation.instance in order to allow backend reexecution of deleted objects

# lets encrypt: DNS vs HTTP challange
# lets enctypt: autorenew

# Warning websites with ssl options without https protocol

# Schedule cancellation

# Multiple domains wordpress

# Reversion
# Disable/enable SaaS and VPS

# Don't show lines with size 0?
# pending orders with recharge do not show up
# Traffic of disabled accounts doesn't get disabled

# URL encode "Order description" on clone
# Service CLONE METRIC doesn't work

# Show warning when saving order and metricstorage date is inconistent with registered date!
# exclude from change list action, support for multiple exclusion

# breadcrumbs https://orchestra.pangea.org/admin/domains/domain/?account_id=930

with open(file) as handler:
    os.unlink(file)


# Mark transaction process as executed should not override higher transaction states
# Bill amend and related transaction, what to do? allow edit transaction ammount of amends when their are pending execution

# DASHBOARD: Show owned tickets, scheduled actions, maintenance operations (diff domains)

# Add confirmation step on transaction actions like process transaction

# SAVE INISTIAL PASSWORD from all services, and just use it to create the service, never update it

# Don't use system groups for unixmailbackends
