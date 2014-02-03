# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Instance', fields ['daemon', 'host']
        db.delete_unique(u'daemons_instance', ['daemon_id', 'host_id'])

        # Deleting model 'Instance'
        db.delete_table(u'daemons_instance')

        # Deleting model 'Daemon'
        db.delete_table(u'daemons_daemon')

        # Adding model 'Route'
        db.create_table(u'daemons_route', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('backend', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orchestration.Server'])),
            ('match', self.gf('django.db.models.fields.CharField')(default='True', max_length=256, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'daemons', ['Route'])

        # Adding unique constraint on 'Route', fields ['backend', 'host']
        db.create_unique(u'daemons_route', ['backend', 'host_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Route', fields ['backend', 'host']
        db.delete_unique(u'daemons_route', ['backend', 'host_id'])

        # Adding model 'Instance'
        db.create_table(u'daemons_instance', (
            ('router', self.gf('django.db.models.fields.CharField')(default='True', max_length=256, blank=True)),
            ('daemon', self.gf('django.db.models.fields.related.ForeignKey')(related_name='instances', to=orm['daemons.Daemon'])),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orchestration.Server'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'daemons', ['Instance'])

        # Adding unique constraint on 'Instance', fields ['daemon', 'host']
        db.create_unique(u'daemons_instance', ['daemon_id', 'host_id'])

        # Adding model 'Daemon'
        db.create_table(u'daemons_daemon', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('backend', self.gf('django.db.models.fields.CharField')(max_length=256, unique=True)),
        ))
        db.send_create_signal(u'daemons', ['Daemon'])

        # Deleting model 'Route'
        db.delete_table(u'daemons_route')


    models = {
        u'daemons.route': {
            'Meta': {'unique_together': "(('backend', 'host'),)", 'object_name': 'Route'},
            'backend': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orchestration.Server']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'match': ('django.db.models.fields.CharField', [], {'default': "'True'", 'max_length': '256', 'blank': 'True'})
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