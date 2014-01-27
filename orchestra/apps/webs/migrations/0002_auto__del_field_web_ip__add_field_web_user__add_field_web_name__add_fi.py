# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Web.ip'
        db.delete_column(u'webs_web', 'ip')

        # Adding field 'Web.user'
        db.add_column(u'webs_web', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='webs', to=orm['auth.User']),
                      keep_default=False)

        # Adding field 'Web.name'
        db.add_column(u'webs_web', 'name',
                      self.gf('django.db.models.fields.CharField')(default='random', unique=True, max_length=128),
                      keep_default=False)

        # Adding field 'Web.type'
        db.add_column(u'webs_web', 'type',
                      self.gf('django.db.models.fields.CharField')(default='php5', max_length=32),
                      keep_default=False)

        # Adding field 'Web.is_active'
        db.add_column(u'webs_web', 'is_active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Removing M2M table for field names on 'Web'
        db.delete_table(db.shorten_name(u'webs_web_names'))

        # Adding M2M table for field domains on 'Web'
        m2m_table_name = db.shorten_name(u'webs_web_domains')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('web', models.ForeignKey(orm[u'webs.web'], null=False)),
            ('name', models.ForeignKey(orm[u'names.name'], null=False))
        ))
        db.create_unique(m2m_table_name, ['web_id', 'name_id'])


    def backwards(self, orm):
        # Adding field 'Web.ip'
        db.add_column(u'webs_web', 'ip',
                      self.gf('django.db.models.fields.GenericIPAddressField')(default='all', max_length=39, null=True),
                      keep_default=False)

        # Deleting field 'Web.user'
        db.delete_column(u'webs_web', 'user_id')

        # Deleting field 'Web.name'
        db.delete_column(u'webs_web', 'name')

        # Deleting field 'Web.type'
        db.delete_column(u'webs_web', 'type')

        # Deleting field 'Web.is_active'
        db.delete_column(u'webs_web', 'is_active')

        # Adding M2M table for field names on 'Web'
        m2m_table_name = db.shorten_name(u'webs_web_names')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('web', models.ForeignKey(orm[u'webs.web'], null=False)),
            ('name', models.ForeignKey(orm[u'names.name'], null=False))
        ))
        db.create_unique(m2m_table_name, ['web_id', 'name_id'])

        # Removing M2M table for field domains on 'Web'
        db.delete_table(db.shorten_name(u'webs_web_domains'))


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

    complete_apps = ['webs']