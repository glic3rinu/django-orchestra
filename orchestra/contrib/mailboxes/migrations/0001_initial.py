# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import orchestra.contrib.mailboxes.validators
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Address name, left blank for a <i>catch-all</i> address', validators=[orchestra.contrib.mailboxes.validators.validate_emailname], verbose_name='name', blank=True, max_length=64)),
                ('forward', models.CharField(help_text='Space separated email addresses or mailboxes', validators=[orchestra.contrib.mailboxes.validators.validate_forward], verbose_name='forward', blank=True, max_length=256)),
                ('account', models.ForeignKey(related_name='addresses', to=settings.AUTH_USER_MODEL, verbose_name='Account')),
                ('domain', models.ForeignKey(related_name='addresses', to='domains.Domain', verbose_name='domain')),
            ],
            options={
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='Autoresponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(verbose_name='subject', max_length=256)),
                ('message', models.TextField(verbose_name='message')),
                ('enabled', models.BooleanField(default=False, verbose_name='enabled')),
                ('address', models.OneToOneField(related_name='autoresponse', to='mailboxes.Address', verbose_name='address')),
            ],
        ),
        migrations.CreateModel(
            name='Mailbox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid mailbox name.')], verbose_name='name', max_length=64)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('filtering', models.CharField(choices=[('REJECT', 'Reject spam (X-Spam-Score&ge;9)'), ('REDIRECT', 'Archive spam (X-Spam-Score&ge;9)'), ('DISABLE', 'Disable'), ('CUSTOM', 'Custom filtering')], default='REDIRECT', max_length=16)),
                ('custom_filtering', models.TextField(help_text='Arbitrary email filtering in sieve language. This overrides any automatic junk email filtering', validators=[orchestra.contrib.mailboxes.validators.validate_sieve], verbose_name='filtering', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('account', models.ForeignKey(related_name='mailboxes', to=settings.AUTH_USER_MODEL, verbose_name='account')),
            ],
            options={
                'verbose_name_plural': 'mailboxes',
            },
        ),
        migrations.AddField(
            model_name='address',
            name='mailboxes',
            field=models.ManyToManyField(related_name='addresses', to='mailboxes.Mailbox', verbose_name='mailboxes', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='address',
            unique_together=set([('name', 'domain')]),
        ),
    ]
