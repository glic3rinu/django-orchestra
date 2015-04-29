# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.models.fields
import orchestra.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Miscellaneous',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', orchestra.models.fields.NullableCharField(null=True, verbose_name='identifier', unique=True, help_text='A unique identifier for this service.', max_length=256)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('amount', models.PositiveIntegerField(verbose_name='amount', default=1)),
                ('is_active', models.BooleanField(help_text='Designates whether this service should be treated as active. Unselect this instead of deleting services.', verbose_name='active', default=True)),
                ('account', models.ForeignKey(verbose_name='account', to=settings.AUTH_USER_MODEL, related_name='miscellaneous')),
            ],
            options={
                'verbose_name_plural': 'miscellaneous',
            },
        ),
        migrations.CreateModel(
            name='MiscService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='name', unique=True, validators=[orchestra.core.validators.validate_name], max_length=32, help_text='Raw name used for internal referenciation, i.e. service match definition')),
                ('verbose_name', models.CharField(verbose_name='verbose name', max_length=256, blank=True, help_text='Human readable name')),
                ('description', models.TextField(verbose_name='description', blank=True, help_text='Optional description')),
                ('has_identifier', models.BooleanField(help_text='Designates if this service has a <b>unique text</b> field that identifies it or not.', verbose_name='has identifier', default=True)),
                ('has_amount', models.BooleanField(help_text='Designates whether this service has <tt>amount</tt> property or not.', verbose_name='has amount', default=False)),
                ('is_active', models.BooleanField(help_text='Whether new instances of this service can be created or not. Unselect this instead of deleting services.', verbose_name='active', default=True)),
            ],
        ),
        migrations.AddField(
            model_name='miscellaneous',
            name='service',
            field=models.ForeignKey(verbose_name='service', to='miscellaneous.MiscService', related_name='instances'),
        ),
    ]
