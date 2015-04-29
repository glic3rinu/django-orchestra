# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('services', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetricStorage',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('value', models.DecimalField(max_digits=16, decimal_places=2, verbose_name='value')),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('registered_on', models.DateField(default=django.utils.timezone.now, verbose_name='registered')),
                ('cancelled_on', models.DateField(blank=True, null=True, verbose_name='cancelled')),
                ('billed_on', models.DateField(blank=True, null=True, verbose_name='billed')),
                ('billed_until', models.DateField(blank=True, null=True, verbose_name='billed until')),
                ('ignore', models.BooleanField(default=False, verbose_name='ignore')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='orders', verbose_name='account')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('service', models.ForeignKey(to='services.Service', related_name='orders', verbose_name='service')),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.AddField(
            model_name='metricstorage',
            name='order',
            field=models.ForeignKey(to='orders.Order', related_name='metrics', verbose_name='order'),
        ),
    ]
