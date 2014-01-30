# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MailDomain'
        db.create_table(u'mails_maildomain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['names.Domain'], unique=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='HOSTED', max_length=20)),
        ))
        db.send_create_signal(u'mails', ['MailDomain'])

        # Adding model 'Mailbox'
        db.create_table(u'mails_mailbox', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('emailname', self.gf('django.db.models.fields.CharField')(max_length=23)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mails.MailDomain'])),
            ('home', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256, blank=True)),
        ))
        db.send_create_signal(u'mails', ['Mailbox'])

        # Adding unique constraint on 'Mailbox', fields ['emailname', 'domain']
        db.create_unique(u'mails_mailbox', ['emailname', 'domain_id'])

        # Adding model 'MailAlias'
        db.create_table(u'mails_mailalias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('emailname', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mails.MailDomain'])),
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'mails', ['MailAlias'])

        # Adding unique constraint on 'MailAlias', fields ['emailname', 'domain']
        db.create_unique(u'mails_mailalias', ['emailname', 'domain_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'MailAlias', fields ['emailname', 'domain']
        db.delete_unique(u'mails_mailalias', ['emailname', 'domain_id'])

        # Removing unique constraint on 'Mailbox', fields ['emailname', 'domain']
        db.delete_unique(u'mails_mailbox', ['emailname', 'domain_id'])

        # Deleting model 'MailDomain'
        db.delete_table(u'mails_maildomain')

        # Deleting model 'Mailbox'
        db.delete_table(u'mails_mailbox')

        # Deleting model 'MailAlias'
        db.delete_table(u'mails_mailalias')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'mails.mailalias': {
            'Meta': {'unique_together': "(('emailname', 'domain'),)", 'object_name': 'MailAlias'},
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mails.MailDomain']"}),
            'emailname': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'mails.mailbox': {
            'Meta': {'unique_together': "(('emailname', 'domain'),)", 'object_name': 'Mailbox'},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mails.MailDomain']"}),
            'emailname': ('django.db.models.fields.CharField', [], {'max_length': '23'}),
            'home': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'mails.maildomain': {
            'Meta': {'object_name': 'MailDomain'},
            'domain': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['names.Domain']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'HOSTED'", 'max_length': '20'})
        },
        u'names.domain': {
            'Meta': {'object_name': 'Domain'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        }
    }

    complete_apps = ['mails']