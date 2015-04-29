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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=256, validators=[orchestra.contrib.domains.validators.validate_domain_name, orchestra.contrib.domains.validators.validate_allowed_domain], verbose_name='name', help_text='Domain or subdomain name.')),
                ('serial', models.IntegerField(default=orchestra.contrib.domains.utils.generate_zone_serial, verbose_name='serial', help_text='Serial number')),
                ('account', models.ForeignKey(related_name='domains', help_text='Automatically selected for subdomains.', to=settings.AUTH_USER_MODEL, verbose_name='Account', blank=True)),
                ('top', models.ForeignKey(null=True, to='domains.Domain', editable=False, related_name='subdomain_set')),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('ttl', models.CharField(help_text='Record TTL, defaults to 1h', max_length=8, validators=[orchestra.contrib.domains.validators.validate_zone_interval], verbose_name='TTL', blank=True)),
                ('type', models.CharField(max_length=32, verbose_name='type', choices=[('MX', 'MX'), ('NS', 'NS'), ('CNAME', 'CNAME'), ('A', 'A (IPv4 address)'), ('AAAA', 'AAAA (IPv6 address)'), ('SRV', 'SRV'), ('TXT', 'TXT'), ('SOA', 'SOA')])),
                ('value', models.CharField(max_length=256, verbose_name='value')),
                ('domain', models.ForeignKey(related_name='records', to='domains.Domain', verbose_name='domain')),
            ],
        ),
    ]
