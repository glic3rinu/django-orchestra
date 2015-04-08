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
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='name', validators=[orchestra.core.validators.validate_name], help_text='Default list address &lt;name&gt;@lists.pangea.org')),
                ('address_name', models.CharField(blank=True, verbose_name='address name', validators=[orchestra.core.validators.validate_name], max_length=128)),
                ('admin_email', models.EmailField(max_length=254, verbose_name='admin email', help_text='Administration email address')),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.')),
                ('account', models.ForeignKey(related_name='lists', verbose_name='Account', to=settings.AUTH_USER_MODEL)),
                ('address_domain', models.ForeignKey(blank=True, null=True, verbose_name='address domain', to='domains.Domain')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='list',
            unique_together=set([('address_name', 'address_domain')]),
        ),
    ]
