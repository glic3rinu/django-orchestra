# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import orchestra.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('domains', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, validators=[orchestra.core.validators.validate_name], unique=True, verbose_name='name', help_text='Default list address &lt;name&gt;@lists.orchestra.lan')),
                ('address_name', models.CharField(max_length=128, validators=[orchestra.core.validators.validate_name], verbose_name='address name', blank=True)),
                ('admin_email', models.EmailField(max_length=254, verbose_name='admin email', help_text='Administration email address')),
                ('is_active', models.BooleanField(default=True, verbose_name='active', help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.')),
                ('account', models.ForeignKey(related_name='lists', to=settings.AUTH_USER_MODEL, verbose_name='Account')),
                ('address_domain', models.ForeignKey(null=True, blank=True, to='domains.Domain', verbose_name='address domain')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='list',
            unique_together=set([('address_name', 'address_domain')]),
        ),
    ]
