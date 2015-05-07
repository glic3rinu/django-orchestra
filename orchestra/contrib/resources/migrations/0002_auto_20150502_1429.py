# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrontabSchedule',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('minute', models.CharField(max_length=64, verbose_name='minute', default='*')),
                ('hour', models.CharField(max_length=64, verbose_name='hour', default='*')),
                ('day_of_week', models.CharField(max_length=64, verbose_name='day of week', default='*')),
                ('day_of_month', models.CharField(max_length=64, verbose_name='day of month', default='*')),
                ('month_of_year', models.CharField(max_length=64, verbose_name='month of year', default='*')),
            ],
            options={
                'verbose_name': 'crontab',
                'ordering': ('month_of_year', 'day_of_month', 'day_of_week', 'hour', 'minute'),
                'verbose_name_plural': 'crontabs',
            },
        ),
    ]
