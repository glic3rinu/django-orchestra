# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Domain'
        db.create_table(u'emails_domain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domain', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['names.Name'], unique=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='HOSTED', max_length=20)),
        ))
        db.send_create_signal(u'emails', ['Domain'])

        # Adding model 'Mailbox'
        db.create_table(u'emails_mailbox', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('emailname', self.gf('django.db.models.fields.CharField')(max_length=23)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emails.Domain'])),
            ('home', self.gf('django.db.models.fields.CharField')(default='/home', unique=True, max_length=256, blank=True)),
        ))
        db.send_create_signal(u'emails', ['Mailbox'])

        # Adding unique constraint on 'Mailbox', fields ['emailname', 'domain']
        db.create_unique(u'emails_mailbox', ['emailname', 'domain_id'])

        # Adding model 'Alias'
        db.create_table(u'emails_alias', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('emailname', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emails.Domain'])),
            ('destination', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'emails', ['Alias'])

        # Adding unique constraint on 'Alias', fields ['emailname', 'domain']
        db.create_unique(u'emails_alias', ['emailname', 'domain_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Alias', fields ['emailname', 'domain']
        db.delete_unique(u'emails_alias', ['emailname', 'domain_id'])

        # Removing unique constraint on 'Mailbox', fields ['emailname', 'domain']
        db.delete_unique(u'emails_mailbox', ['emailname', 'domain_id'])

        # Deleting model 'Domain'
        db.delete_table(u'emails_domain')

        # Deleting model 'Mailbox'
        db.delete_table(u'emails_mailbox')

        # Deleting model 'Alias'
        db.delete_table(u'emails_alias')


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
        u'emails.alias': {
            'Meta': {'unique_together': "(('emailname', 'domain'),)", 'object_name': 'Alias'},
            'destination': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['emails.Domain']"}),
            'emailname': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'emails.domain': {
            'Meta': {'object_name': 'Domain'},
            'domain': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['names.Name']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'HOSTED'", 'max_length': '20'})
        },
        u'emails.mailbox': {
            'Meta': {'unique_together': "(('emailname', 'domain'),)", 'object_name': 'Mailbox'},
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['emails.Domain']"}),
            'emailname': ('django.db.models.fields.CharField', [], {'max_length': '23'}),
            'home': ('django.db.models.fields.CharField', [], {'default': "'/home'", 'unique': 'True', 'max_length': '256', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'names.name': {
            'Meta': {'object_name': 'Name'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        }
    }

    complete_apps = ['emails']
