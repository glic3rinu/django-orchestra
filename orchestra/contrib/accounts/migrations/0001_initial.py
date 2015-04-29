# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.utils.timezone
import django.contrib.auth.models


class Migration(migrations.Migration):

#    dependencies = [
#        ('systemusers', '__first__'),
#    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('username', models.CharField(validators=[django.core.validators.RegexValidator('^[\\w.-]+$', 'Enter a valid username.', 'invalid')], help_text='Required. 64 characters or fewer. Letters, digits and ./-/_ only.', unique=True, max_length=32, verbose_name='username')),
                ('short_name', models.CharField(blank=True, max_length=64, verbose_name='short name')),
                ('full_name', models.CharField(max_length=256, verbose_name='full name')),
                ('email', models.EmailField(help_text='Used for password recovery', verbose_name='email address', max_length=254)),
                ('type', models.CharField(choices=[('INDIVIDUAL', 'Individual'), ('ASSOCIATION', 'Association'), ('CUSTOMER', 'Customer'), ('STAFF', 'Staff'), ('FRIEND', 'Friend')], default='INDIVIDUAL', max_length=32, verbose_name='type')),
                ('language', models.CharField(choices=[('CA', 'Catalan'), ('ES', 'Spanish'), ('EN', 'English')], default='CA', max_length=2, verbose_name='language')),
                ('comments', models.TextField(blank=True, max_length=256, verbose_name='comments')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('main_systemuser', models.ForeignKey(related_name='accounts_main', null=True, editable=False, to='systemusers.SystemUser')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
