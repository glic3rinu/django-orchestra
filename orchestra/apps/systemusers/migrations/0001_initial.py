# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SystemUser'
        db.create_table(u'systemusers_systemuser', (
            ('uid', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['systemusers.SystemGroup'])),
            ('home', self.gf('django.db.models.fields.CharField')(default='/home/', max_length=256)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('shell', self.gf('django.db.models.fields.CharField')(default='/bin/false', max_length=256)),
            ('ftp_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'systemusers', ['SystemUser'])

        # Adding model 'SystemGroup'
        db.create_table(u'systemusers_systemgroup', (
            ('gid', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'systemusers', ['SystemGroup'])

        # Adding M2M table for field users on 'SystemGroup'
        m2m_table_name = db.shorten_name(u'systemusers_systemgroup_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('systemgroup', models.ForeignKey(orm[u'systemusers.systemgroup'], null=False)),
            ('systemuser', models.ForeignKey(orm[u'systemusers.systemuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['systemgroup_id', 'systemuser_id'])


    def backwards(self, orm):
        # Deleting model 'SystemUser'
        db.delete_table(u'systemusers_systemuser')

        # Deleting model 'SystemGroup'
        db.delete_table(u'systemusers_systemgroup')

        # Removing M2M table for field users on 'SystemGroup'
        db.delete_table(db.shorten_name(u'systemusers_systemgroup_users'))


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
        u'systemusers.systemgroup': {
            'Meta': {'object_name': 'SystemGroup'},
            'gid': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['systemusers.SystemUser']", 'null': 'True', 'blank': 'True'})
        },
        u'systemusers.systemuser': {
            'Meta': {'object_name': 'SystemUser'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ftp_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['systemusers.SystemGroup']"}),
            'home': ('django.db.models.fields.CharField', [], {'default': "'/home/'", 'max_length': '256'}),
            'shell': ('django.db.models.fields.CharField', [], {'default': "'/bin/false'", 'max_length': '256'}),
            'uid': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['systemusers']