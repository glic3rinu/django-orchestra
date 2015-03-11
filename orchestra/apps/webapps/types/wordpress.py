from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.apps.databases.models import Database, DatabaseUser
from orchestra.plugins.forms import PluginDataForm
from orchestra.utils.python import random_ascii

from .. import settings

from .php import (PHPAppType, PHPFCGIDApp, PHPFPMApp, PHPFCGIDAppForm, PHPFCGIDAppSerializer,
        PHPFPMAppForm, PHPFPMAppSerializer)


class WordPressAbstractAppForm(PluginDataForm):
    db_name = forms.CharField(label=_("Database name"),
            help_text=_("Database used for this webapp."))
    db_user = forms.CharField(label=_("Database user"),)
    db_pass = forms.CharField(label=_("Database user password"),
            help_text=_("Initial database password."))


class WordPressAbstractAppSerializer(serializers.Serializer):
    db_name = serializers.CharField(label=_("Database name"), required=False)
    db_user = serializers.CharField(label=_("Database user"), required=False)
    db_pass = serializers.CharField(label=_("Database user password"), required=False)


class WordPressAbstractApp(object):
    icon = 'orchestra/icons/apps/WordPress.png'
    change_readonly_fileds = ('db_name', 'db_user', 'db_pass',)
    help_text = _("Visit http://&lt;domain.lan&gt;/wp-admin/install.php to finish the installation.")
    
    def get_db_name(self):
        db_name = 'wp_%s_%s' % (self.instance.name, self.instance.account)
        # Limit for mysql database names
        return db_name[:65]
    
    def get_db_user(self):
        db_name = self.get_db_name()
        # Limit for mysql user names
        return db_name[:16]
    
    def get_db_pass(self):
        return random_ascii(10)
    
    def validate(self):
        super(WordPressAbstractApp, self).validate()
        create = not self.instance.pk
        if create:
            db = Database(name=self.get_db_name(), account=self.instance.account)
            user = DatabaseUser(username=self.get_db_user(), password=self.get_db_pass(),
                    account=self.instance.account)
            for obj in (db, user):
                try:
                    obj.full_clean()
                except ValidationError as e:
                    raise ValidationError({
                        'name': e.messages,
                    })
    
    def save(self):
        create = not self.instance.pk
        if create:
            db_name = self.get_db_name()
            db_user = self.get_db_user()
            db_pass = self.get_db_pass()
            db = Database.objects.create(name=db_name, account=self.instance.account)
            user = DatabaseUser(username=db_user, account=self.instance.account)
            user.set_password(db_pass)
            user.save()
            db.users.add(user)
            self.instance.data = {
                'db_name': db_name,
                'db_user': db_user,
                'db_pass': db_pass,
            }
        else:
            # Trigger related backends
            for related in self.get_related():
                related.save()
        
    def delete(self):
        for related in self.get_related():
            related.delete()
    
    def get_related(self):
        related = []
        account = self.instance.account
        try:
            db_user = account.databaseusers.get(username=self.instance.data.get('db_user'))
        except DatabaseUser.DoesNotExist:
            pass
        else:
            related.append(db_user)
        try:
            db = account.databases.get(name=self.instance.data.get('db_name'))
        except Database.DoesNotExist:
            pass
        else:
            related.append(db)
        return related


class WordPressFPMApp(WordPressAbstractApp, PHPFPMApp):
    name = 'wordpress-fpm'
    php_execution = PHPAppType.FPM
    verbose_name = "WordPress (FPM)"
    serializer = type('WordPressFPMSerializer',
            (WordPressAbstractAppSerializer, PHPFPMAppSerializer), {})
    change_form = type('WordPressFPMForm',
            (WordPressAbstractAppForm, PHPFPMAppForm), {})


class WordPressFCGIDApp(WordPressAbstractApp, PHPFCGIDApp):
    name = 'wordpress-fcgid'
    php_execution = PHPAppType.FCGID
    verbose_name = "WordPress (FCGID)"
    serializer = type('WordPressFCGIDSerializer',
            (WordPressAbstractAppSerializer, PHPFCGIDAppSerializer), {})
    change_form = type('WordPressFCGIDForm',
            (WordPressAbstractAppForm, PHPFCGIDAppForm), {})
