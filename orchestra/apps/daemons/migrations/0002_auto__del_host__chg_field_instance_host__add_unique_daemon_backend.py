# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Host'
        db.delete_table(u'daemons_host')


        # Changing field 'Instance.host'
        db.alter_column(u'daemons_instance', 'host_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orchestration.Server']))
        # Adding unique constraint on 'Daemon', fields ['backend']
        db.create_unique(u'daemons_daemon', ['backend'])


    def backwards(self, orm):
        # Removing unique constraint on 'Daemon', fields ['backend']
        db.delete_unique(u'daemons_daemon', ['backend'])

        # Adding model 'Host'
        db.create_table(u'daemons_host', (
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('os', self.gf('django.db.models.fields.CharField')(default='LINUX', max_length=32)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, unique=True)),
        ))
        db.send_create_signal(u'daemons', ['Host'])


        # Changing field 'Instance.host'
        db.alter_column(u'daemons_instance', 'host_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['daemons.Host']))

    models = {
        u'daemons.daemon': {
            'Meta': {'object_name': 'Daemon'},
            'backend': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'hosts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['orchestration.Server']", 'through': u"orm['daemons.Instance']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'daemons.instance': {
            'Meta': {'unique_together': "(('daemon', 'host'),)", 'object_name': 'Instance'},
            'daemon': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instances'", 'to': u"orm['daemons.Daemon']"}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orchestration.Server']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'router': ('django.db.models.fields.CharField', [], {'default': "'True'", 'max_length': '256', 'blank': 'True'})
        },
        u'orchestration.server': {
            'Meta': {'object_name': 'Server'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'os': ('django.db.models.fields.CharField', [], {'default': "'LINUX'", 'max_length': '32'})
        }
    }

    complete_apps = ['daemons']