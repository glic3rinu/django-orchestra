# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('systemusers', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and ./-/_ only.', unique=True, max_length=64, verbose_name='username', validators=[django.core.validators.RegexValidator(b'^[\\w.-]+$', 'Enter a valid username.', b'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(help_text='Used for password recovery', max_length=75, verbose_name='email address')),
                ('type', models.CharField(default=b'INDIVIDUAL', max_length=32, verbose_name='type', choices=[(b'INDIVIDUAL', 'Individual'), (b'ASSOCIATION', 'Association'), (b'CUSTOMER', 'Customer'), (b'STAFF', 'Staff')])),
                ('language', models.CharField(default=b'ca', max_length=2, verbose_name='language', choices=[(b'ca', 'Catalan'), (b'es', 'Spanish'), (b'en', 'English')])),
                ('comments', models.TextField(max_length=256, verbose_name='comments', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('main_systemuser', models.ForeignKey(related_name='accounts_main', to='systemusers.SystemUser', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
