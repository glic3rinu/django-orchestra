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
                ('name', models.CharField(verbose_name='name', validators=[orchestra.contrib.mailboxes.validators.validate_emailname], blank=True, help_text='Address name, left blank for a <i>catch-all</i> address', max_length=64)),
                ('forward', models.CharField(verbose_name='forward', validators=[orchestra.contrib.mailboxes.validators.validate_forward], blank=True, help_text='Space separated email addresses or mailboxes', max_length=256)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='addresses', verbose_name='Account')),
                ('domain', models.ForeignKey(to='domains.Domain', related_name='addresses', verbose_name='domain')),
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
                ('enabled', models.BooleanField(verbose_name='enabled', default=False)),
                ('address', models.OneToOneField(to='mailboxes.Address', related_name='autoresponse', verbose_name='address')),
            ],
        ),
        migrations.CreateModel(
            name='Mailbox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(verbose_name='name', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid mailbox name.')], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=64, unique=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('filtering', models.CharField(choices=[('CUSTOM', 'Custom filtering'), ('REDIRECT', 'Archive spam (X-Spam-Score&ge;9)'), ('DISABLE', 'Disable'), ('REJECT', 'Reject spam (X-Spam-Score&ge;9)')], max_length=16, default='REDIRECT')),
                ('custom_filtering', models.TextField(verbose_name='filtering', validators=[orchestra.contrib.mailboxes.validators.validate_sieve], blank=True, help_text='Arbitrary email filtering in sieve language. This overrides any automatic junk email filtering')),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='mailboxes', verbose_name='account')),
            ],
            options={
                'verbose_name_plural': 'mailboxes',
            },
        ),
        migrations.AddField(
            model_name='address',
            name='mailboxes',
            field=models.ManyToManyField(verbose_name='mailboxes', to='mailboxes.Mailbox', blank=True, related_name='addresses'),
        ),
        migrations.AlterUniqueTogether(
            name='address',
            unique_together=set([('name', 'domain')]),
        ),
    ]
