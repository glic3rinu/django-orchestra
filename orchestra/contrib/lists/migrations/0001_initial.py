# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', help_text='Default list address &lt;name&gt;@lists.pangea.org', validators=[orchestra.core.validators.validate_name], max_length=128, unique=True)),
                ('address_name', models.CharField(verbose_name='address name', blank=True, validators=[orchestra.core.validators.validate_name], max_length=128)),
                ('admin_email', models.EmailField(verbose_name='admin email', help_text='Administration email address', max_length=254)),
                ('is_active', models.BooleanField(verbose_name='active', help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.', default=True)),
                ('account', models.ForeignKey(verbose_name='Account', related_name='lists', to=settings.AUTH_USER_MODEL)),
                ('address_domain', models.ForeignKey(verbose_name='address domain', null=True, blank=True, to='domains.Domain')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='list',
            unique_together=set([('address_name', 'address_domain')]),
        ),
    ]
