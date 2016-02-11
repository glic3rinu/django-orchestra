from django import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.contrib.databases.models import Database, DatabaseUser
from orchestra.forms.widgets import SpanWidget
from orchestra.utils.python import random_ascii

from .php import PHPApp, PHPAppForm, PHPAppSerializer


class CMSAppForm(PHPAppForm):
    db_name = forms.CharField(label=_("Database name"),
            help_text=_("Database exclusively used for this webapp."))
    db_user = forms.CharField(label=_("Database user"),
            help_text=_("Database user exclusively used for this webapp."))
    password = forms.CharField(label=_("Password"),
            help_text=_("Initial database and WordPress admin password.<br>"
                        "Subsequent changes to the admin password will not be reflected."))
    
    def __init__(self, *args, **kwargs):
        super(CMSAppForm, self).__init__(*args, **kwargs)
        if self.instance:
            data = self.instance.data
            # DB link
            db_name = data.get('db_name')
            db_id = data.get('db_id')
            db_url = reverse('admin:databases_database_change', args=(db_id,))
            db_link = mark_safe('<a href="%s">%s</a>' % (db_url, db_name))
            self.fields['db_name'].widget = SpanWidget(original=db_name, display=db_link)
            # DB user link
            db_user = data.get('db_user')
            db_user_id = data.get('db_user_id')
            db_user_url = reverse('admin:databases_databaseuser_change', args=(db_user_id,))
            db_user_link = mark_safe('<a href="%s">%s</a>' % (db_user_url, db_user))
            self.fields['db_user'].widget = SpanWidget(original=db_user, display=db_user_link)


class CMSAppSerializer(PHPAppSerializer):
    db_name = serializers.CharField(label=_("Database name"), required=False)
    db_user = serializers.CharField(label=_("Database user"), required=False)
    password = serializers.CharField(label=_("Password"), required=False)
    db_id = serializers.IntegerField(label=_("Database ID"), required=False)
    db_user_id = serializers.IntegerField(label=_("Database user ID"), required=False)


class CMSApp(PHPApp):
    """ Abstract AppType with common CMS functionality """
    serializer = CMSAppSerializer
    change_form = CMSAppForm
    change_readonly_fields = ('db_name', 'db_user', 'password',)
    db_type = Database.MYSQL
    abstract = True
    db_prefix = 'cms_'
    
    def get_db_name(self):
        db_name = '%s%s_%s' % (self.db_prefix, self.instance.name, self.instance.account)
        # Limit for mysql database names
        return db_name[:65]
    
    def get_db_user(self):
        db_name = self.get_db_name()
        # Limit for mysql user names
        return db_name[:16]
    
    def get_password(self):
        return random_ascii(10)
    
    def validate(self):
        super(CMSApp, self).validate()
        create = not self.instance.pk
        if create:
            db = Database(name=self.get_db_name(), account=self.instance.account, type=self.db_type)
            user = DatabaseUser(username=self.get_db_user(), password=self.get_password(),
                    account=self.instance.account, type=self.db_type)
            for obj in (db, user):
                try:
                    obj.full_clean()
                except ValidationError as e:
                    raise ValidationError({
                        'name': e.messages,
                    })
    
    def save(self):
        db_name = self.get_db_name()
        db_user = self.get_db_user()
        password = self.get_password()
        db, db_created = self.instance.account.databases.get_or_create(name=db_name, type=self.db_type)
        if db_created:
            user = DatabaseUser(username=db_user, account=self.instance.account, type=self.db_type)
            user.set_password(password)
            user.save()
            db.users.add(user)
            self.instance.data.update({
                'db_name': db_name,
                'db_user': db_user,
                'password': password,
                'db_id': db.id,
                'db_user_id': user.id,
            })
