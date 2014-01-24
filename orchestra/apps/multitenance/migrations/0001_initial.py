# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Application'
        db.create_table(u'multitenance_application', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.TextField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'multitenance', ['Application'])

        # Adding model 'Tenant'
        db.create_table(u'multitenance_tenant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['multitenance.Application'], unique=True)),
            ('data', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'multitenance', ['Tenant'])


    def backwards(self, orm):
        # Deleting model 'Application'
        db.delete_table(u'multitenance_application')

        # Deleting model 'Tenant'
        db.delete_table(u'multitenance_tenant')


    models = {
        u'multitenance.application': {
            'Meta': {'object_name': 'Application'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'max_length': '256'})
        },
        u'multitenance.tenant': {
            'Meta': {'object_name': 'Tenant'},
            'application': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['multitenance.Application']", 'unique': 'True'}),
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['multitenance']