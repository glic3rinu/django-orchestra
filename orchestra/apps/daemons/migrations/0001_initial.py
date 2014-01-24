# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Daemon'
        db.create_table(u'daemons_daemon', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('backend', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'daemons', ['Daemon'])

        # Adding model 'Host'
        db.create_table(u'daemons_host', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('os', self.gf('django.db.models.fields.CharField')(default='LINUX', max_length=32)),
        ))
        db.send_create_signal(u'daemons', ['Host'])

        # Adding model 'Instance'
        db.create_table(u'daemons_instance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('daemon', self.gf('django.db.models.fields.related.ForeignKey')(related_name='instances', to=orm['daemons.Daemon'])),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['daemons.Host'])),
            ('router', self.gf('django.db.models.fields.CharField')(default='True', max_length=256, blank=True)),
        ))
        db.send_create_signal(u'daemons', ['Instance'])

        # Adding unique constraint on 'Instance', fields ['daemon', 'host']
        db.create_unique(u'daemons_instance', ['daemon_id', 'host_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Instance', fields ['daemon', 'host']
        db.delete_unique(u'daemons_instance', ['daemon_id', 'host_id'])

        # Deleting model 'Daemon'
        db.delete_table(u'daemons_daemon')

        # Deleting model 'Host'
        db.delete_table(u'daemons_host')

        # Deleting model 'Instance'
        db.delete_table(u'daemons_instance')


    models = {
        u'daemons.daemon': {
            'Meta': {'object_name': 'Daemon'},
            'backend': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'hosts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['daemons.Host']", 'through': u"orm['daemons.Instance']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'daemons.host': {
            'Meta': {'object_name': 'Host'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'os': ('django.db.models.fields.CharField', [], {'default': "'LINUX'", 'max_length': '32'})
        },
        u'daemons.instance': {
            'Meta': {'unique_together': "(('daemon', 'host'),)", 'object_name': 'Instance'},
            'daemon': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instances'", 'to': u"orm['daemons.Daemon']"}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['daemons.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'router': ('django.db.models.fields.CharField', [], {'default': "'True'", 'max_length': '256', 'blank': 'True'})
        }
    }

    complete_apps = ['daemons']