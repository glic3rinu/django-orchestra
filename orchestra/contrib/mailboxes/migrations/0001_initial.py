# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.contrib.mailboxes.validators
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('domains', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=64, validators=[orchestra.contrib.mailboxes.validators.validate_emailname], help_text='Address name, left blank for a <i>catch-all</i> address', verbose_name='name', blank=True)),
                ('forward', models.CharField(max_length=256, validators=[orchestra.contrib.mailboxes.validators.validate_forward], help_text='Space separated email addresses or mailboxes', verbose_name='forward', blank=True)),
                ('account', models.ForeignKey(related_name='addresses', verbose_name='Account', to=settings.AUTH_USER_MODEL)),
                ('domain', models.ForeignKey(related_name='addresses', verbose_name='domain', to='domains.Domain')),
            ],
            options={
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='Autoresponse',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('subject', models.CharField(max_length=256, verbose_name='subject')),
                ('message', models.TextField(verbose_name='message')),
                ('enabled', models.BooleanField(default=False, verbose_name='enabled')),
                ('address', models.OneToOneField(related_name='autoresponse', verbose_name='address', to='mailboxes.Address')),
            ],
        ),
        migrations.CreateModel(
            name='Mailbox',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid mailbox name.')], max_length=64, unique=True, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', verbose_name='name')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('filtering', models.CharField(default='REDIRECT', max_length=16, choices=[('DISABLE', 'Disable'), ('CUSTOM', 'Custom filtering'), ('REDIRECT', 'Archive spam'), ('REJECT', 'Reject spam')])),
                ('custom_filtering', models.TextField(validators=[orchestra.contrib.mailboxes.validators.validate_sieve], help_text='Arbitrary email filtering in sieve language. This overrides any automatic junk email filtering', verbose_name='filtering', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('account', models.ForeignKey(related_name='mailboxes', verbose_name='account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'mailboxes',
            },
        ),
        migrations.AddField(
            model_name='address',
            name='mailboxes',
            field=models.ManyToManyField(related_name='addresses', verbose_name='mailboxes', blank=True, to='mailboxes.Mailbox'),
        ),
        migrations.AlterUniqueTogether(
            name='address',
            unique_together=set([('name', 'domain')]),
        ),
    ]
