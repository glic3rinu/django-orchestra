# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
from django.conf import settings
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Miscellaneous',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('identifier', orchestra.models.fields.NullableCharField(max_length=256, unique=True, verbose_name='identifier', null=True, help_text='A unique identifier for this service.')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('amount', models.PositiveIntegerField(default=1, verbose_name='amount')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this service should be treated as active. Unselect this instead of deleting services.', verbose_name='active')),
                ('account', models.ForeignKey(verbose_name='account', to=settings.AUTH_USER_MODEL, related_name='miscellaneous')),
            ],
            options={
                'verbose_name_plural': 'miscellaneous',
            },
        ),
        migrations.CreateModel(
            name='MiscService',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=32, validators=[orchestra.core.validators.validate_name], unique=True, verbose_name='name', help_text='Raw name used for internal referenciation, i.e. service match definition')),
                ('verbose_name', models.CharField(blank=True, max_length=256, verbose_name='verbose name', help_text='Human readable name')),
                ('description', models.TextField(blank=True, help_text='Optional description', verbose_name='description')),
                ('has_identifier', models.BooleanField(default=True, help_text='Designates if this service has a <b>unique text</b> field that identifies it or not.', verbose_name='has identifier')),
                ('has_amount', models.BooleanField(default=False, help_text='Designates whether this service has <tt>amount</tt> property or not.', verbose_name='has amount')),
                ('is_active', models.BooleanField(default=True, help_text='Whether new instances of this service can be created or not. Unselect this instead of deleting services.', verbose_name='active')),
            ],
        ),
        migrations.AddField(
            model_name='miscellaneous',
            name='service',
            field=models.ForeignKey(verbose_name='service', to='miscellaneous.MiscService', related_name='instances'),
        ),
    ]
