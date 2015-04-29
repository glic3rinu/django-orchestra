# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('services', '__first__'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetricStorage',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('value', models.DecimalField(decimal_places=2, max_digits=16, verbose_name='value')),
                ('created_on', models.DateField(auto_now_add=True, verbose_name='created')),
                ('updated_on', models.DateTimeField(verbose_name='updated')),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('registered_on', models.DateField(default=django.utils.timezone.now, verbose_name='registered')),
                ('cancelled_on', models.DateField(blank=True, verbose_name='cancelled', null=True)),
                ('billed_on', models.DateField(blank=True, verbose_name='billed', null=True)),
                ('billed_until', models.DateField(blank=True, verbose_name='billed until', null=True)),
                ('ignore', models.BooleanField(default=False, verbose_name='ignore')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('account', models.ForeignKey(verbose_name='account', related_name='orders', to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('service', models.ForeignKey(verbose_name='service', related_name='orders', to='services.Service')),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.AddField(
            model_name='metricstorage',
            name='order',
            field=models.ForeignKey(verbose_name='order', related_name='metrics', to='orders.Order'),
        ),
    ]
