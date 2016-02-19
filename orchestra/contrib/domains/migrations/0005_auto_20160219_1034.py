# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import orchestra.contrib.domains.validators


class Migration(migrations.Migration):

    dependencies = [
        ('domains', '0004_auto_20150720_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='name',
            field=models.CharField(max_length=256, validators=[orchestra.contrib.domains.validators.validate_domain_name, orchestra.contrib.domains.validators.validate_allowed_domain], db_index=True, verbose_name='name', unique=True, help_text='Domain or subdomain name.'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='top',
            field=models.ForeignKey(editable=False, verbose_name='top domain', related_name='subdomain_set', to='domains.Domain', null=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='type',
            field=models.CharField(max_length=32, verbose_name='type', choices=[('MX', 'MX'), ('NS', 'NS'), ('CNAME', 'CNAME'), ('A', 'A (IPv4 address)'), ('AAAA', 'AAAA (IPv6 address)'), ('SRV', 'SRV'), ('TXT', 'TXT'), ('SPF', 'SPF'), ('SOA', 'SOA')]),
        ),
    ]
