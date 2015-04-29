# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import django.utils.timezone
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        # Permissions and contenttypes
        ('auth', '0006_require_contenttypes_0002'),
        ('systemusers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(blank=True, verbose_name='last login', null=True)),
                ('username', models.CharField(help_text='Required. 64 characters or fewer. Letters, digits and ./-/_ only.', unique=True, validators=[django.core.validators.RegexValidator('^[\\w.-]+$', 'Enter a valid username.', 'invalid')], max_length=32, verbose_name='username')),
                ('short_name', models.CharField(blank=True, verbose_name='short name', max_length=64)),
                ('full_name', models.CharField(verbose_name='full name', max_length=256)),
                ('email', models.EmailField(help_text='Used for password recovery', max_length=254, verbose_name='email address')),
                ('type', models.CharField(verbose_name='type', choices=[('INDIVIDUAL', 'Individual'), ('ASSOCIATION', 'Association'), ('CUSTOMER', 'Customer'), ('COMPANY', 'Company'), ('PUBLICBODY', 'Public body'), ('STAFF', 'Staff'), ('FRIEND', 'Friend')], max_length=32, default='INDIVIDUAL')),
                ('language', models.CharField(verbose_name='language', choices=[('EN', 'English')], max_length=2, default='EN')),
                ('comments', models.TextField(blank=True, verbose_name='comments', max_length=256)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('is_active', models.BooleanField(help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('main_systemuser', models.ForeignKey(to='systemusers.SystemUser', editable=False, null=True, related_name='accounts_main')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
