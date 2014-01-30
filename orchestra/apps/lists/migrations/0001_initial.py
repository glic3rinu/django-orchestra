# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    from ..settings import LISTS_DOMAIN_MODEL
    app_name = LISTS_DOMAIN_MODEL.split('.')[0]
    depends_on = (
        (app_name, "0001_initial"),
    )

    def forwards(self, orm):
        # Adding model 'List'
        db.create_table(u'lists_list', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mails.MailDomain'])),
            ('admin', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'lists', ['List'])

        # Adding unique constraint on 'List', fields ['name', 'domain']
        db.create_unique(u'lists_list', ['name', 'domain_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'List', fields ['name', 'domain']
        db.delete_unique(u'lists_list', ['name', 'domain_id'])

        # Deleting model 'List'
        db.delete_table(u'lists_list')


    models = {
        u'lists.list': {
            'Meta': {'unique_together': "(('name', 'domain'),)", 'object_name': 'List'},
            'admin': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mails.MailDomain']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'mails.maildomain': {
            'Meta': {'object_name': 'MailDomain'},
            'domain': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['names.Name']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'HOSTED'", 'max_length': '20'})
        },
        u'names.name': {
            'Meta': {'object_name': 'Name'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        }
    }

    complete_apps = ['lists']
