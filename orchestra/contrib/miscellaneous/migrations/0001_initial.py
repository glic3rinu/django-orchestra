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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('identifier', orchestra.models.fields.NullableCharField(max_length=256, help_text='A unique identifier for this service.', unique=True, null=True, verbose_name='identifier')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('amount', models.PositiveIntegerField(default=1, verbose_name='amount')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this service should be treated as active. Unselect this instead of deleting services.', verbose_name='active')),
                ('account', models.ForeignKey(related_name='miscellaneous', verbose_name='account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'miscellaneous',
            },
        ),
        migrations.CreateModel(
            name='MiscService',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=32, help_text='Raw name used for internal referenciation, i.e. service match definition', unique=True, verbose_name='name', validators=[orchestra.core.validators.validate_name])),
                ('verbose_name', models.CharField(max_length=256, help_text='Human readable name', blank=True, verbose_name='verbose name')),
                ('description', models.TextField(help_text='Optional description', blank=True, verbose_name='description')),
                ('has_identifier', models.BooleanField(default=True, help_text='Designates if this service has a <b>unique text</b> field that identifies it or not.', verbose_name='has identifier')),
                ('has_amount', models.BooleanField(default=False, help_text='Designates whether this service has <tt>amount</tt> property or not.', verbose_name='has amount')),
                ('is_active', models.BooleanField(default=True, help_text='Whether new instances of this service can be created or not. Unselect this instead of deleting services.', verbose_name='active')),
            ],
        ),
        migrations.AddField(
            model_name='miscellaneous',
            name='service',
            field=models.ForeignKey(related_name='instances', verbose_name='service', to='miscellaneous.MiscService'),
        ),
    ]
