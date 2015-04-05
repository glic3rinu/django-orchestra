# -*- coding: utf-8 -*-

from django.db import models, migrations
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
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('amount', models.PositiveIntegerField(default=1, verbose_name='amount')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this service should be treated as active. Unselect this instead of deleting services.', verbose_name='active')),
                ('account', models.ForeignKey(related_name='miscellaneous', verbose_name='account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'miscellaneous',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MiscService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Raw name used for internal referenciation, i.e. service match definition', unique=True, max_length=32, verbose_name='name', validators=[orchestra.core.validators.validate_name])),
                ('verbose_name', models.CharField(help_text='Human readable name', max_length=256, verbose_name='verbose name', blank=True)),
                ('description', models.TextField(help_text='Optional description', verbose_name='description', blank=True)),
                ('has_amount', models.BooleanField(default=False, help_text='Designates whether this service has <tt>amount</tt> property or not.', verbose_name='has amount')),
                ('is_active', models.BooleanField(default=True, help_text='Whether new instances of this service can be created or not. Unselect this instead of deleting services.', verbose_name='active')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='miscellaneous',
            name='service',
            field=models.ForeignKey(related_name='instances', verbose_name='service', to='miscellaneous.MiscService'),
            preserve_default=True,
        ),
    ]
