# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('state', models.CharField(choices=[('QUEUED', 'Queued'), ('SENT', 'Sent'), ('DEFERRED', 'Deferred'), ('FAILED', 'Failes')], default='QUEUED', verbose_name='State', max_length=16)),
                ('priority', models.PositiveIntegerField(choices=[(0, 'Critical (not queued)'), (1, 'High'), (2, 'Normal'), (3, 'Low')], default=2, verbose_name='Priority')),
                ('to_address', models.CharField(max_length=256)),
                ('from_address', models.CharField(max_length=256)),
                ('subject', models.CharField(max_length=256, verbose_name='subject')),
                ('content', models.TextField(verbose_name='content')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('retries', models.PositiveIntegerField(default=0, verbose_name='retries')),
                ('last_retry', models.DateTimeField(auto_now=True, verbose_name='last try')),
            ],
        ),
        migrations.CreateModel(
            name='SMTPLog',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('result', models.CharField(choices=[('SUCCESS', 'Success'), ('FAILURE', 'Failure')], default='SUCCESS', max_length=16)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('log_message', models.TextField()),
                ('message', models.ForeignKey(to='mailer.Message', editable=False, related_name='logs')),
            ],
        ),
    ]
