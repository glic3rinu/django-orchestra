from django import forms
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
        self.fields['username'].label = _("Name")
        base_domain = self.plugin.site_name_base_domain
        help_text = _("Admin URL http://&lt;name&gt;.{}/admin/").format(base_domain)
        self.fields['site_name'].help_text = help_text


class PHPListChangeForm(PHPListForm):
#    site_name = forms.CharField(widget=widgets.ShowTextWidget, required=False)
    db_name = forms.CharField(label=_("Database name"),
            help_text=_("Database used for this webapp."))
    
    def __init__(self, *args, **kwargs):
        super(PHPListChangeForm, self).__init__(*args, **kwargs)
        site_name = self.instance.get_site_name()
        admin_url = "http://%s/admin/" % site_name
        help_text = _("Admin URL <a href={0}>{0}</a>").format(admin_url)
        self.fields['site_name'].help_text = help_text


class PHPListSerializer(serializers.Serializer):
    db_name = serializers.CharField(label=_("Database name"), required=False)


class PHPListService(SoftwareService):
    name = 'phplist'
    verbose_name = "phpList"
    form = PHPListForm
    change_form = PHPListChangeForm
    change_readonly_fileds = ('db_name',)
    serializer = PHPListSerializer
    icon = 'orchestra/icons/apps/Phplist.png'
    site_name_base_domain = settings.SAAS_PHPLIST_BASE_DOMAIN
    
    def get_db_name(self):
        db_name = 'phplist_mu_%s' % self.instance.username
        # Limit for mysql database names
        return db_name[:65]
    
    def get_db_user(self):
        return settings.SAAS_PHPLIST_DB_NAME
    
    def validate(self):
        super(PHPListService, self).validate()
        create = not self.instance.pk
        if create:
            db = Database(name=self.get_db_name(), account=self.instance.account)
            try:
                db.full_clean()
            except ValidationError as e:
                raise ValidationError({
                    'name': e.messages,
                })
    
    def save(self):
        db_name = self.get_db_name()
        db_user = self.get_db_user()
        db, db_created = Database.objects.get_or_create(name=db_name, account=self.instance.account)
        user = DatabaseUser.objects.get(username=db_user)
        db.users.add(user)
        self.instance.data = {
            'db_name': db_name,
        }
        if not db_created:
            # Trigger related backends
            for related in self.get_related():
                related.save(update_fields=[])
        
    def delete(self):
        for related in self.get_related():
            related.delete()
    
    def get_related(self):
        related = []
        account = self.instance.account
        try:
            db = account.databases.get(name=self.instance.data.get('db_name'))
        except Database.DoesNotExist:
            pass
        else:
            related.append(db)
        return related
