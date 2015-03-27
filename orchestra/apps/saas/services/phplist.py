from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.apps.databases.models import Database, DatabaseUser
from orchestra.forms import widgets
from orchestra.plugins.forms import PluginDataForm

from .. import settings
from .options import SoftwareService, SoftwareServiceForm


class PHPListForm(SoftwareServiceForm):
    admin_username = forms.CharField(label=_("Admin username"), required=False,
            widget=widgets.ReadOnlyWidget('admin'))
    
    def __init__(self, *args, **kwargs):
        super(PHPListForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = _("Site name")
        base_domain = self.plugin.site_base_domain
        help_text = _("Admin URL http://&lt;site_name&gt;.{}/admin/").format(base_domain)
        self.fields['site_url'].help_text = help_text


class PHPListChangeForm(PHPListForm):
    database = forms.CharField(label=_("Database"), required=False,
            help_text=_("Database used for this webapp."))
    
    def __init__(self, *args, **kwargs):
        super(PHPListChangeForm, self).__init__(*args, **kwargs)
        site_domain = self.instance.get_site_domain()
        admin_url = "http://%s/admin/" % site_domain
        help_text = _("Admin URL <a href={0}>{0}</a>").format(admin_url)
        self.fields['site_url'].help_text = help_text
        # DB link
        db = self.instance.database
        db_url = reverse('admin:databases_database_change', args=(db.pk,))
        db_link = mark_safe('<a href="%s">%s</a>' % (db_url, db.name))
        self.fields['database'].widget = widgets.ReadOnlyWidget(db.name, db_link)


class PHPListService(SoftwareService):
    name = 'phplist'
    verbose_name = "phpList"
    form = PHPListForm
    change_form = PHPListChangeForm
    icon = 'orchestra/icons/apps/Phplist.png'
    site_base_domain = settings.SAAS_PHPLIST_BASE_DOMAIN
    
    def get_db_name(self):
        db_name = 'phplist_mu_%s' % self.instance.name
        # Limit for mysql database names
        return db_name[:65]
    
    def get_db_user(self):
        return settings.SAAS_PHPLIST_DB_NAME
    
    def get_account(self):
        return type(self.instance.account).get_main()
    
    def validate(self):
        super(PHPListService, self).validate()
        create = not self.instance.pk
        if create:
            account = self.get_account()
            db = Database(name=self.get_db_name(), account=account)
            try:
                db.full_clean()
            except ValidationError as e:
                raise ValidationError({
                    'name': e.messages,
                })
    
    def save(self):
        db_name = self.get_db_name()
        db_user = self.get_db_user()
        account = self.get_account()
        db, db_created = account.databases.get_or_create(name=db_name, type=Database.MYSQL)
        user = DatabaseUser.objects.get(username=db_user)
        db.users.add(user)
        self.instance.database_id = db.pk
