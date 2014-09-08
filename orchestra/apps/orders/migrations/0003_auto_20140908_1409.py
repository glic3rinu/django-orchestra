# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '__first__'),
        ('orders', '0002_service_nominal_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'basic', max_length=128, verbose_name='plan', choices=[(b'basic', 'Basic'), (b'advanced', 'Advanced')])),
                ('account', models.ForeignKey(related_name=b'plans', verbose_name='account', to='accounts.Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('plan', models.CharField(blank=True, max_length=128, verbose_name='plan', choices=[(b'', 'default'), (b'basic', 'Basic'), (b'advanced', 'Advanced')])),
                ('quantity', models.PositiveIntegerField(null=True, verbose_name='quantity', blank=True)),
                ('value', models.DecimalField(verbose_name='value', max_digits=12, decimal_places=2)),
                ('service', models.ForeignKey(related_name=b'rates', verbose_name='service', to='orders.Service')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='rate',
            unique_together=set([('service', 'plan', 'quantity')]),
        ),
    ]
