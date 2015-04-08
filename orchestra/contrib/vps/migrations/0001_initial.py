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
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('hostname', models.CharField(verbose_name='hostname', max_length=256, validators=[orchestra.core.validators.validate_hostname], unique=True)),
                ('type', models.CharField(default='openvz', verbose_name='type', max_length=64, choices=[('openvz', 'OpenVZ container')])),
                ('template', models.CharField(default='debian7', verbose_name='template', max_length=64, choices=[('debian7', 'Debian 7 - Wheezy')])),
                ('password', models.CharField(verbose_name='password', help_text='<TT>root</TT> password of this virtual machine', max_length=128)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Account', related_name='vpss')),
            ],
            options={
                'verbose_name': 'VPS',
                'verbose_name_plural': 'VPSs',
            },
        ),
    ]
