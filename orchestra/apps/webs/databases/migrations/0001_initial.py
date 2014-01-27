# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'databases_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('select', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('delete', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('insert', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('update', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('create', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('drop', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('alter', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('index', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('grant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('refer', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('lock', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=41)),
        ))
        db.send_create_signal(u'databases', ['User'])

        # Adding model 'Database'
        db.create_table(u'databases_database', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('select', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('delete', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('insert', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('update', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('create', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('drop', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('alter', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('index', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('grant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('refer', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('lock', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['databases.User'])),
        ))
        db.send_create_signal(u'databases', ['Database'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'databases_user')

        # Deleting model 'Database'
        db.delete_table(u'databases_database')


    models = {
        u'databases.database': {
            'Meta': {'object_name': 'Database'},
            'alter': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'create': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'delete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'drop': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'grant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'insert': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lock': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'refer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'select': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'update': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['databases.User']"})
        },
        u'databases.user': {
            'Meta': {'object_name': 'User'},
            'alter': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'create': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'delete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'drop': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'grant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'insert': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lock': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '41'}),
            'refer': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'select': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'update': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        }
    }

    complete_apps = ['databases']