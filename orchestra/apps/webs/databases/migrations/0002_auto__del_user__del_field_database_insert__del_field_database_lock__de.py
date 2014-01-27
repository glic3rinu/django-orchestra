# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'databases_user')

        # Deleting field 'Database.insert'
        db.delete_column(u'databases_database', 'insert')

        # Deleting field 'Database.lock'
        db.delete_column(u'databases_database', 'lock')

        # Deleting field 'Database.update'
        db.delete_column(u'databases_database', 'update')

        # Deleting field 'Database.user'
        db.delete_column(u'databases_database', 'user_id')

        # Deleting field 'Database.select'
        db.delete_column(u'databases_database', 'select')

        # Deleting field 'Database.index'
        db.delete_column(u'databases_database', 'index')

        # Deleting field 'Database.name'
        db.delete_column(u'databases_database', 'name')

        # Deleting field 'Database.grant'
        db.delete_column(u'databases_database', 'grant')

        # Deleting field 'Database.create'
        db.delete_column(u'databases_database', 'create')

        # Deleting field 'Database.drop'
        db.delete_column(u'databases_database', 'drop')

        # Deleting field 'Database.refer'
        db.delete_column(u'databases_database', 'refer')

        # Deleting field 'Database.alter'
        db.delete_column(u'databases_database', 'alter')

        # Deleting field 'Database.delete'
        db.delete_column(u'databases_database', 'delete')

        # Adding field 'Database.web'
        db.add_column(u'databases_database', 'web',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='databases', to=orm['webs.Web']),
                      keep_default=False)

        # Adding field 'Database.username'
        db.add_column(u'databases_database', 'username',
                      self.gf('django.db.models.fields.CharField')(default='random', unique=True, max_length=128),
                      keep_default=False)

        # Adding field 'Database.password'
        db.add_column(u'databases_database', 'password',
                      self.gf('django.db.models.fields.CharField')(default='random', max_length=64),
                      keep_default=False)

        # Adding field 'Database.type'
        db.add_column(u'databases_database', 'type',
                      self.gf('django.db.models.fields.CharField')(default='mysql', max_length=32),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'User'
        db.create_table(u'databases_user', (
            ('insert', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('lock', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('update', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=41)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('select', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('index', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True)),
            ('grant', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('drop', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('refer', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('alter', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('delete', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'databases', ['User'])

        # Adding field 'Database.insert'
        db.add_column(u'databases_database', 'insert',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Database.lock'
        db.add_column(u'databases_database', 'lock',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Database.update'
        db.add_column(u'databases_database', 'update',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Database.user'
        db.add_column(u'databases_database', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['databases.User']),
                      keep_default=False)

        # Adding field 'Database.select'
        db.add_column(u'databases_database', 'select',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Database.index'
        db.add_column(u'databases_database', 'index',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Database.name'
        db.add_column(u'databases_database', 'name',
                      self.gf('django.db.models.fields.CharField')(default='random', max_length=128, unique=True),
                      keep_default=False)

        # Adding field 'Database.grant'
        db.add_column(u'databases_database', 'grant',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Database.create'
        db.add_column(u'databases_database', 'create',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Database.drop'
        db.add_column(u'databases_database', 'drop',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Database.refer'
        db.add_column(u'databases_database', 'refer',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Database.alter'
        db.add_column(u'databases_database', 'alter',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Database.delete'
        db.add_column(u'databases_database', 'delete',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Deleting field 'Database.web'
        db.delete_column(u'databases_database', 'web_id')

        # Deleting field 'Database.username'
        db.delete_column(u'databases_database', 'username')

        # Deleting field 'Database.password'
        db.delete_column(u'databases_database', 'password')

        # Deleting field 'Database.type'
        db.delete_column(u'databases_database', 'type')


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
        u'databases.database': {
            'Meta': {'object_name': 'Database'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'mysql'", 'max_length': '32'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'web': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'databases'", 'to': u"orm['webs.Web']"})
        },
        u'names.name': {
            'Meta': {'object_name': 'Name'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'webs.web': {
            'Meta': {'object_name': 'Web'},
            'directives': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'domains': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['names.Name']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {'default': '80'}),
            'root': ('django.db.models.fields.CharField', [], {'default': "'/var/www/%(name)s/'", 'max_length': '256', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'php5'", 'max_length': '32'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'webs'", 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['databases']