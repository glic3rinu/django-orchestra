# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Zone'
        db.create_table(u'zones_zone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('hostmaster', self.gf('django.db.models.fields.EmailField')(default='hostmaster@example.com', max_length=75)),
            ('ttl', self.gf('django.db.models.fields.CharField')(default='1h', max_length=8, null=True, blank=True)),
            ('serial', self.gf('django.db.models.fields.IntegerField')(default=2014012401)),
            ('refresh', self.gf('django.db.models.fields.CharField')(default='1d', max_length=8)),
            ('retry', self.gf('django.db.models.fields.CharField')(default='2h', max_length=8)),
            ('expiration', self.gf('django.db.models.fields.CharField')(default='4w', max_length=8)),
            ('min_caching_time', self.gf('django.db.models.fields.CharField')(default='1h', max_length=8)),
        ))
        db.send_create_signal(u'zones', ['Zone'])

        # Adding model 'Record'
        db.create_table(u'zones_record', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zone', self.gf('django.db.models.fields.related.ForeignKey')(related_name='records', to=orm['zones.Zone'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'zones', ['Record'])


    def backwards(self, orm):
        # Deleting model 'Zone'
        db.delete_table(u'zones_zone')

        # Deleting model 'Record'
        db.delete_table(u'zones_record')


    models = {
        u'zones.record': {
            'Meta': {'object_name': 'Record'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'records'", 'to': u"orm['zones.Zone']"})
        },
        u'zones.zone': {
            'Meta': {'object_name': 'Zone'},
            'expiration': ('django.db.models.fields.CharField', [], {'default': "'4w'", 'max_length': '8'}),
            'hostmaster': ('django.db.models.fields.EmailField', [], {'default': "'hostmaster@example.com'", 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'min_caching_time': ('django.db.models.fields.CharField', [], {'default': "'1h'", 'max_length': '8'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'refresh': ('django.db.models.fields.CharField', [], {'default': "'1d'", 'max_length': '8'}),
            'retry': ('django.db.models.fields.CharField', [], {'default': "'2h'", 'max_length': '8'}),
            'serial': ('django.db.models.fields.IntegerField', [], {'default': '2014012401'}),
            'ttl': ('django.db.models.fields.CharField', [], {'default': "'1h'", 'max_length': '8', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['zones']