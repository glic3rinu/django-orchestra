# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetricStorage',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('value', models.DecimalField(verbose_name='value', decimal_places=2, max_digits=16)),
                ('created_on', models.DateField(verbose_name='created', auto_now_add=True)),
                ('updated_on', models.DateTimeField(verbose_name='updated')),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('registered_on', models.DateField(verbose_name='registered', default=django.utils.timezone.now)),
                ('cancelled_on', models.DateField(blank=True, verbose_name='cancelled', null=True)),
                ('billed_on', models.DateField(blank=True, verbose_name='billed', null=True)),
                ('billed_until', models.DateField(blank=True, verbose_name='billed until', null=True)),
                ('ignore', models.BooleanField(verbose_name='ignore', default=False)),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('account', models.ForeignKey(related_name='orders', verbose_name='account', to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('service', models.ForeignKey(related_name='orders', verbose_name='service', to='services.Service')),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.AddField(
            model_name='metricstorage',
            name='order',
            field=models.ForeignKey(related_name='metrics', verbose_name='order', to='orders.Order'),
        ),
    ]
