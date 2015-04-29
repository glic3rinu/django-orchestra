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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('hostname', models.CharField(unique=True, verbose_name='hostname', validators=[orchestra.core.validators.validate_hostname], max_length=256)),
                ('type', models.CharField(choices=[('openvz', 'OpenVZ container')], verbose_name='type', default='openvz', max_length=64)),
                ('template', models.CharField(choices=[('debian7', 'Debian 7 - Wheezy')], verbose_name='template', default='debian7', max_length=64)),
                ('password', models.CharField(verbose_name='password', help_text='<TT>root</TT> password of this virtual machine', max_length=128)),
                ('account', models.ForeignKey(verbose_name='Account', related_name='vpss', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'VPS',
                'verbose_name_plural': 'VPSs',
            },
        ),
    ]
