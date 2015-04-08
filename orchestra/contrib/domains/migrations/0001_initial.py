# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.contrib.domains.validators
from django.conf import settings
import orchestra.contrib.domains.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(validators=[orchestra.contrib.domains.validators.validate_domain_name, orchestra.contrib.domains.validators.validate_allowed_domain], help_text='Domain or subdomain name.', unique=True, max_length=256, verbose_name='name')),
                ('serial', models.IntegerField(help_text='Serial number', default=orchestra.contrib.domains.utils.generate_zone_serial, verbose_name='serial')),
                ('account', models.ForeignKey(help_text='Automatically selected for subdomains.', blank=True, verbose_name='Account', to=settings.AUTH_USER_MODEL, related_name='domains')),
                ('top', models.ForeignKey(related_name='subdomain_set', null=True, to='domains.Domain', editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('ttl', models.CharField(validators=[orchestra.contrib.domains.validators.validate_zone_interval], help_text='Record TTL, defaults to 1h', blank=True, max_length=8, verbose_name='TTL')),
                ('type', models.CharField(choices=[('MX', 'MX'), ('NS', 'NS'), ('CNAME', 'CNAME'), ('A', 'A (IPv4 address)'), ('AAAA', 'AAAA (IPv6 address)'), ('SRV', 'SRV'), ('TXT', 'TXT'), ('SOA', 'SOA')], max_length=32, verbose_name='type')),
                ('value', models.CharField(max_length=256, verbose_name='value')),
                ('domain', models.ForeignKey(verbose_name='domain', to='domains.Domain', related_name='records')),
            ],
        ),
    ]
