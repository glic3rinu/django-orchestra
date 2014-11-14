# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(help_text='Required. 64 characters or fewer. Letters, digits and ./-/_ only.', unique=True, max_length=64, verbose_name='username', validators=[django.core.validators.RegexValidator(b'^[\\w.-]+$', 'Enter a valid username.', b'invalid')])),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('home', models.CharField(help_text="Home directory relative to account's ~main_user", max_length=256, verbose_name='home', blank=True)),
                ('shell', models.CharField(default=b'/dev/null', max_length=32, verbose_name='shell', choices=[(b'/dev/null', 'No shell, FTP only'), (b'/bin/rssh', 'No shell, SFTP/RSYNC only'), (b'/bin/bash', b'/bin/bash'), (b'/bin/sh', b'/bin/sh')])),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('account', models.ForeignKey(related_name='systemusers', verbose_name='Account', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(help_text='A new group will be created for the user. Which additional groups would you like them to be a member of?', to='systemusers.SystemUser', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
