# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import orchestra.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemUser',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('username', models.CharField(verbose_name='username', help_text='Required. 64 characters or fewer. Letters, digits and ./-/_ only.', validators=[orchestra.core.validators.validate_username], max_length=32, unique=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('home', models.CharField(verbose_name='home', help_text='Starting location when login with this no-shell user.', blank=True, max_length=256)),
                ('directory', models.CharField(verbose_name='directory', help_text="Optional directory relative to user's home.", blank=True, max_length=256)),
                ('shell', models.CharField(verbose_name='shell', choices=[('/dev/null', 'No shell, FTP only'), ('/bin/rssh', 'No shell, SFTP/RSYNC only'), ('/bin/bash', '/bin/bash'), ('/bin/sh', '/bin/sh')], default='/dev/null', max_length=32)),
                ('is_active', models.BooleanField(verbose_name='active', help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.', default=True)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='systemusers', verbose_name='Account')),
                ('groups', models.ManyToManyField(help_text='A new group will be created for the user. Which additional groups would you like them to be a member of?', blank=True, to='systemusers.SystemUser')),
            ],
        ),
    ]
