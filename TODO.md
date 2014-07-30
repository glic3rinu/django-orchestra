TODO
====

* scape strings before executing scripts in order to prevent exploits: django templates automatically scapes things. Most important is to ensuer that all escape ' to &quot
* Optimize SSH: pool, `UseDNS no`
* Don't store passwords and other service parameters that can be changed by the services i.e. mailman, vps etc. Find an execution mechanism that trigger `change_password()`

* abort transaction on orchestration when `state == TIMEOUT` ?
* filter and other user.is_main refactoring 
* use format_html_join for orchestration email alerts

* generic form for change and display passwords and crack change password form
* enforce an emergency email contact and account to contact contacts about problems when mailserver is down

* add `BackendLog` retry action
* move invoice contact to invoices app?
* wrapper around reverse('admin:....') `link()` and `link_factory()`
* PHPbBckendMiixin with get_php_ini
* Apache: `IncludeOptional /etc/apache2/extra-vhos[t]/account-site-custom.con[f]`
* rename account.user to primary_user
* webmail identities and addresses
* cached -> cached_property
* user.roles.mailbox its awful when combined with addresses:
    * address.mailboxes filter by account is crap in admin and api
    * address.mailboxes api needs a mailbox object endpoint (not nested user)
    * Its not intuitive, users expect to create mailboxes, not users!
    * Mailbox is something tangible, not a role!
* System user vs virtual user:
    * system user automatically hast @domain.com address :(

* use Code: https://github.com/django/django/blob/master/django/forms/forms.py#L415 for domain.refresh_serial()
* Permissions .filter_queryset()


* git deploy in addition to FTP?
* env vars instead of multiple settings files: https://devcenter.heroku.com/articles/config-vars ?
* optional chroot shell?

* make sure prefetch_related() is used correctly 
Remember that, as always with QuerySets, any subsequent chained methods which imply a different database query will ignore previously cached results, and retrieve data using a fresh database query. 
* profile select_related vs prefetch_related

* use HTTP OPTIONS instead of configuration endpoint, or rename to settings?

* Log changes from rest api (serialized objects)


* passlib; nano /usr/local/lib/python2.7/dist-packages/passlib/ext/django/utils.py SortedDict -> collections.OrderedDict
* pip install pyinotify

* create custom field that returns backend python objects

* Timezone awareness on monitoring system (reading server-side logs with different TZ than orchestra) maybe a settings value? (use UTC internally, timezone.localtime() when interacting with servers)

* EMAIL backend operations which contain stderr messages (because under certain failures status code is still 0)


* Settings dictionary like DRF2 in order to better override large settings like WEBSITES_APPLICATIONS.etc


* DOCUMENT: orchestration.middleware: we need to know when an operation starts and ends in order to perform bulk server updates and also to wait for related objects to be saved (base object is saved first and then related)
            orders.signales: we perform changes right away because data model state can change under monitoring and other periodik task, and we should keep orders consistency under any situation.
                             dependency collector with max_recursion that matches the number of dots on service.match and service.metric


* Be consistent with dates:
    * created_on date
    * created_at datetime

at + clock time, midnight, noon- At 3:30 p.m., At 4:01, At noon


* backend logs with hal logo
* Use logs for storing monitored values
* set_password orchestration method?
