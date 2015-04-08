# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('databases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaaS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('service', models.CharField(verbose_name='service', max_length=32, choices=[('bscw', 'BSCW'), ('DokuWikiService', 'Dowkuwiki'), ('DrupalService', 'Drupal'), ('gitlab', 'GitLab'), ('MoodleService', 'Moodle'), ('seafile', 'SeaFile'), ('WordPressService', 'WordPress'), ('phplist', 'phpList')])),
                ('name', models.CharField(help_text='Required. 64 characters or fewer. Letters, digits and ./-/_ only.', max_length=64, validators=[orchestra.core.validators.validate_username], verbose_name='Name')),
                ('is_active', models.BooleanField(help_text='Designates whether this service should be treated as active. ', verbose_name='active', default=True)),
                ('data', jsonfield.fields.JSONField(help_text='Extra information dependent of each service.', verbose_name='data', default={})),
                ('account', models.ForeignKey(related_name='saas', to=settings.AUTH_USER_MODEL, verbose_name='account')),
                ('database', models.ForeignKey(to='databases.Database', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'SaaS',
                'verbose_name_plural': 'SaaS',
            },
        ),
        migrations.AlterUniqueTogether(
            name='saas',
            unique_together=set([('name', 'service')]),
        ),
    ]
