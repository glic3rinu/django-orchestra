# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('author_name', models.CharField(verbose_name='author name', max_length=256, blank=True)),
                ('content', models.TextField(verbose_name='content')),
                ('created_on', models.DateTimeField(verbose_name='created on', auto_now_add=True)),
                ('author', models.ForeignKey(related_name='ticket_messages', to=settings.AUTH_USER_MODEL, verbose_name='author')),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(unique=True, verbose_name='name', max_length=128)),
                ('verbose_name', models.CharField(verbose_name='verbose_name', max_length=128, blank=True)),
                ('default', models.BooleanField(default=False, verbose_name='default')),
                ('notify', orchestra.models.fields.MultiSelectField(choices=[('SUPPORT', 'Support tickets'), ('ADMIN', 'Administrative'), ('BILLING', 'Billing'), ('TECH', 'Technical'), ('ADDS', 'Announcements'), ('EMERGENCY', 'Emergency contact')], help_text='Contacts to notify by email', verbose_name='notify', blank=True, default=('SUPPORT', 'ADMIN', 'BILLING', 'TECH', 'ADDS', 'EMERGENCY'), max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('creator_name', models.CharField(verbose_name='creator name', max_length=256, blank=True)),
                ('subject', models.CharField(verbose_name='subject', max_length=256)),
                ('description', models.TextField(verbose_name='description')),
                ('priority', models.CharField(choices=[('HIGH', 'High'), ('MEDIUM', 'Medium'), ('LOW', 'Low')], default='MEDIUM', max_length=32, verbose_name='priority')),
                ('state', models.CharField(choices=[('NEW', 'New'), ('IN_PROGRESS', 'In Progress'), ('RESOLVED', 'Resolved'), ('FEEDBACK', 'Feedback'), ('REJECTED', 'Rejected'), ('CLOSED', 'Closed')], default='NEW', max_length=32, verbose_name='state')),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(verbose_name='modified', auto_now=True)),
                ('cc', models.TextField(help_text='emails to send a carbon copy to', verbose_name='CC', blank=True)),
                ('creator', models.ForeignKey(null=True, related_name='tickets_created', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('owner', models.ForeignKey(null=True, related_name='tickets_owned', blank=True, to=settings.AUTH_USER_MODEL, verbose_name='assigned to')),
                ('queue', models.ForeignKey(null=True, related_name='tickets', blank=True, to='issues.Queue')),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='TicketTracker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('ticket', models.ForeignKey(related_name='trackers', to='issues.Ticket', verbose_name='ticket')),
                ('user', models.ForeignKey(related_name='ticket_trackers', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='ticket',
            field=models.ForeignKey(related_name='messages', to='issues.Ticket', verbose_name='ticket'),
        ),
        migrations.AlterUniqueTogether(
            name='tickettracker',
            unique_together=set([('ticket', 'user')]),
        ),
    ]
