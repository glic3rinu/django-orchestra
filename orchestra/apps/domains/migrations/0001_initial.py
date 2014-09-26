# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
import orchestra.apps.domains.validators
import orchestra.apps.domains.utils


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20140909_1850'),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=256, verbose_name='name', validators=[orchestra.core.validators.validate_hostname, orchestra.apps.domains.validators.validate_allowed_domain])),
                ('serial', models.IntegerField(default=orchestra.apps.domains.utils.generate_zone_serial, help_text='Serial number', verbose_name='serial')),
                ('account', models.ForeignKey(related_name=b'domains', verbose_name='Account', blank=True, to='accounts.Account')),
                ('top', models.ForeignKey(related_name=b'subdomains', to='domains.Domain', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=32, verbose_name='type', choices=[(b'MX', b'MX'), (b'NS', b'NS'), (b'CNAME', b'CNAME'), (b'A', 'A (IPv4 address)'), (b'AAAA', 'AAAA (IPv6 address)'), (b'SRV', b'SRV'), (b'TXT', b'TXT'), (b'SOA', b'SOA')])),
                ('value', models.CharField(max_length=256, verbose_name='value')),
                ('domain', models.ForeignKey(related_name=b'records', verbose_name='domain', to='domains.Domain')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
