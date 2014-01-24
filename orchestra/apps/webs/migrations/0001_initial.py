# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Web'
        db.create_table(u'webs_web', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip', self.gf('django.db.models.fields.GenericIPAddressField')(default='all', max_length=39, null=True)),
            ('port', self.gf('django.db.models.fields.PositiveIntegerField')(default=80)),
            ('root', self.gf('django.db.models.fields.CharField')(default='/var/www/%(name)s/', max_length=256, blank=True)),
            ('directives', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'webs', ['Web'])

        # Adding M2M table for field names on 'Web'
        m2m_table_name = db.shorten_name(u'webs_web_names')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('web', models.ForeignKey(orm[u'webs.web'], null=False)),
            ('name', models.ForeignKey(orm[u'names.name'], null=False))
        ))
        db.create_unique(m2m_table_name, ['web_id', 'name_id'])


    def backwards(self, orm):
        # Deleting model 'Web'
        db.delete_table(u'webs_web')

        # Removing M2M table for field names on 'Web'
        db.delete_table(db.shorten_name(u'webs_web_names'))


    models = {
        u'names.name': {
            'Meta': {'object_name': 'Name'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'webs.web': {
            'Meta': {'object_name': 'Web'},
            'directives': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'default': "'all'", 'max_length': '39', 'null': 'True'}),
            'names': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['names.Name']", 'symmetrical': 'False'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {'default': '80'}),
            'root': ('django.db.models.fields.CharField', [], {'default': "'/var/www/%(name)s/'", 'max_length': '256', 'blank': 'True'})
        }
    }

    complete_apps = ['webs']