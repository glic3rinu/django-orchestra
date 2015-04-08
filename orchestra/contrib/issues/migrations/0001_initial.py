# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import orchestra.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('author_name', models.CharField(verbose_name='author name', blank=True, max_length=256)),
                ('content', models.TextField(verbose_name='content')),
                ('created_on', models.DateTimeField(verbose_name='created on', auto_now_add=True)),
                ('author', models.ForeignKey(verbose_name='author', related_name='ticket_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='name', unique=True, max_length=128)),
                ('verbose_name', models.CharField(verbose_name='verbose_name', blank=True, max_length=128)),
                ('default', models.BooleanField(verbose_name='default', default=False)),
                ('notify', orchestra.models.fields.MultiSelectField(blank=True, default=('SUPPORT', 'ADMIN', 'BILLING', 'TECH', 'ADDS', 'EMERGENCY'), choices=[('SUPPORT', 'Support tickets'), ('ADMIN', 'Administrative'), ('BILLING', 'Billing'), ('TECH', 'Technical'), ('ADDS', 'Announcements'), ('EMERGENCY', 'Emergency contact')], help_text='Contacts to notify by email', verbose_name='notify', max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('creator_name', models.CharField(verbose_name='creator name', blank=True, max_length=256)),
                ('subject', models.CharField(verbose_name='subject', max_length=256)),
                ('description', models.TextField(verbose_name='description')),
                ('priority', models.CharField(choices=[('HIGH', 'High'), ('MEDIUM', 'Medium'), ('LOW', 'Low')], verbose_name='priority', default='MEDIUM', max_length=32)),
                ('state', models.CharField(choices=[('NEW', 'New'), ('IN_PROGRESS', 'In Progress'), ('RESOLVED', 'Resolved'), ('FEEDBACK', 'Feedback'), ('REJECTED', 'Rejected'), ('CLOSED', 'Closed')], verbose_name='state', default='NEW', max_length=32)),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(verbose_name='modified', auto_now=True)),
                ('cc', models.TextField(verbose_name='CC', blank=True, help_text='emails to send a carbon copy to')),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='created by', related_name='tickets_created', null=True)),
                ('owner', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='assigned to', related_name='tickets_owned', null=True)),
                ('queue', models.ForeignKey(blank=True, to='issues.Queue', related_name='tickets', null=True)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='TicketTracker',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('ticket', models.ForeignKey(verbose_name='ticket', related_name='trackers', to='issues.Ticket')),
                ('user', models.ForeignKey(verbose_name='user', related_name='ticket_trackers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='ticket',
            field=models.ForeignKey(verbose_name='ticket', related_name='messages', to='issues.Ticket'),
        ),
        migrations.AlterUniqueTogether(
            name='tickettracker',
            unique_together=set([('ticket', 'user')]),
        ),
    ]
