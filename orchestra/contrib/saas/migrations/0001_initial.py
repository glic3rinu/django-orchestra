# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings
import orchestra.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('databases', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SaaS',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('service', models.CharField(max_length=32, verbose_name='service', choices=[('bscw', 'BSCW'), ('DokuWikiService', 'Dowkuwiki'), ('DrupalService', 'Drupal'), ('gitlab', 'GitLab'), ('MoodleService', 'Moodle'), ('seafile', 'SeaFile'), ('WordPressService', 'WordPress'), ('phplist', 'phpList')])),
                ('name', models.CharField(help_text='Required. 64 characters or fewer. Letters, digits and ./-/_ only.', max_length=64, verbose_name='Name', validators=[orchestra.core.validators.validate_username])),
                ('is_active', models.BooleanField(help_text='Designates whether this service should be treated as active. ', verbose_name='active', default=True)),
                ('data', jsonfield.fields.JSONField(help_text='Extra information dependent of each service.', verbose_name='data', default={})),
                ('account', models.ForeignKey(verbose_name='account', to=settings.AUTH_USER_MODEL, related_name='saas')),
                ('database', models.ForeignKey(null=True, blank=True, to='databases.Database')),
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
