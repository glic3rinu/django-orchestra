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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('author_name', models.CharField(blank=True, max_length=256, verbose_name='author name')),
                ('content', models.TextField(verbose_name='content')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('author', models.ForeignKey(related_name='ticket_messages', to=settings.AUTH_USER_MODEL, verbose_name='author')),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='Queue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='name', unique=True)),
                ('verbose_name', models.CharField(blank=True, max_length=128, verbose_name='verbose_name')),
                ('default', models.BooleanField(verbose_name='default', default=False)),
                ('notify', orchestra.models.fields.MultiSelectField(blank=True, max_length=256, help_text='Contacts to notify by email', verbose_name='notify', default=('SUPPORT', 'ADMIN', 'BILLING', 'TECH', 'ADDS', 'EMERGENCY'), choices=[('SUPPORT', 'Support tickets'), ('ADMIN', 'Administrative'), ('BILLING', 'Billing'), ('TECH', 'Technical'), ('ADDS', 'Announcements'), ('EMERGENCY', 'Emergency contact')])),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('creator_name', models.CharField(blank=True, max_length=256, verbose_name='creator name')),
                ('subject', models.CharField(max_length=256, verbose_name='subject')),
                ('description', models.TextField(verbose_name='description')),
                ('priority', models.CharField(max_length=32, default='MEDIUM', verbose_name='priority', choices=[('HIGH', 'High'), ('MEDIUM', 'Medium'), ('LOW', 'Low')])),
                ('state', models.CharField(max_length=32, default='NEW', verbose_name='state', choices=[('NEW', 'New'), ('IN_PROGRESS', 'In Progress'), ('RESOLVED', 'Resolved'), ('FEEDBACK', 'Feedback'), ('REJECTED', 'Rejected'), ('CLOSED', 'Closed')])),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='modified')),
                ('cc', models.TextField(blank=True, help_text='emails to send a carbon copy to', verbose_name='CC')),
                ('creator', models.ForeignKey(related_name='tickets_created', null=True, to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('owner', models.ForeignKey(blank=True, related_name='tickets_owned', null=True, to=settings.AUTH_USER_MODEL, verbose_name='assigned to')),
                ('queue', models.ForeignKey(blank=True, related_name='tickets', null=True, to='issues.Queue')),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='TicketTracker',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
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
