# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.contrib.domains.utils
import orchestra.contrib.domains.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(validators=[orchestra.contrib.domains.validators.validate_domain_name, orchestra.contrib.domains.validators.validate_allowed_domain], max_length=256, help_text='Domain or subdomain name.', unique=True, verbose_name='name')),
                ('serial', models.IntegerField(default=orchestra.contrib.domains.utils.generate_zone_serial, help_text='Serial number', verbose_name='serial')),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Account', blank=True, help_text='Automatically selected for subdomains.', related_name='domains')),
                ('top', models.ForeignKey(to='domains.Domain', null=True, editable=False, related_name='subdomain_set')),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ttl', models.CharField(validators=[orchestra.contrib.domains.validators.validate_zone_interval], max_length=8, help_text='Record TTL, defaults to 1h', blank=True, verbose_name='TTL')),
                ('type', models.CharField(max_length=32, choices=[('MX', 'MX'), ('NS', 'NS'), ('CNAME', 'CNAME'), ('A', 'A (IPv4 address)'), ('AAAA', 'AAAA (IPv6 address)'), ('SRV', 'SRV'), ('TXT', 'TXT'), ('SOA', 'SOA')], verbose_name='type')),
                ('value', models.CharField(max_length=256, verbose_name='value')),
                ('domain', models.ForeignKey(to='domains.Domain', verbose_name='domain', related_name='records')),
            ],
        ),
    ]
