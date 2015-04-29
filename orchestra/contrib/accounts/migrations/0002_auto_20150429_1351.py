# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
import django.core.validators
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('username', models.CharField(max_length=32, verbose_name='username', help_text='Required. 64 characters or fewer. Letters, digits and ./-/_ only.', unique=True, validators=[django.core.validators.RegexValidator('^[\\w.-]+$', 'Enter a valid username.', 'invalid')])),
                ('short_name', models.CharField(max_length=64, verbose_name='short name', blank=True)),
                ('full_name', models.CharField(max_length=256, verbose_name='full name')),
                ('email', models.EmailField(max_length=254, verbose_name='email address', help_text='Used for password recovery')),
                ('type', models.CharField(max_length=32, verbose_name='type', choices=[('INDIVIDUAL', 'Individual'), ('ASSOCIATION', 'Association'), ('CUSTOMER', 'Customer'), ('STAFF', 'Staff'), ('FRIEND', 'Friend')], default='INDIVIDUAL')),
                ('language', models.CharField(max_length=2, verbose_name='language', choices=[('CA', 'Catalan'), ('ES', 'Spanish'), ('EN', 'English')], default='CA')),
                ('comments', models.TextField(max_length=256, verbose_name='comments', blank=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.', default=False)),
                ('is_active', models.BooleanField(verbose_name='active', help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.', default=True)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('main_systemuser', models.ForeignKey(null=True, editable=False, related_name='accounts_main', to='systemusers.SystemUser')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
