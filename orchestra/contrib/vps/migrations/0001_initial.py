# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VPS',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('hostname', models.CharField(unique=True, max_length=256, validators=[orchestra.core.validators.validate_hostname], verbose_name='hostname')),
                ('type', models.CharField(max_length=64, choices=[('openvz', 'OpenVZ container')], verbose_name='type', default='openvz')),
                ('template', models.CharField(max_length=64, choices=[('debian7', 'Debian 7 - Wheezy')], verbose_name='template', default='debian7')),
                ('password', models.CharField(max_length=128, help_text='<TT>root</TT> password of this virtual machine', verbose_name='password')),
                ('account', models.ForeignKey(related_name='vpss', to=settings.AUTH_USER_MODEL, verbose_name='Account')),
            ],
            options={
                'verbose_name_plural': 'VPSs',
                'verbose_name': 'VPS',
            },
        ),
    ]
