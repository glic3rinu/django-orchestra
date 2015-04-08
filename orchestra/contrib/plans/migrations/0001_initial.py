# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('services', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractedPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('account', models.ForeignKey(related_name='plans', verbose_name='account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'plans',
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='name', unique=True, validators=[orchestra.core.validators.validate_name], max_length=32)),
                ('verbose_name', models.CharField(verbose_name='verbose_name', max_length=128, blank=True)),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.')),
                ('is_default', models.BooleanField(verbose_name='default', default=False, help_text='Designates whether this plan is used by default or not.')),
                ('is_combinable', models.BooleanField(verbose_name='combinable', default=True, help_text='Designates whether this plan can be combined with other plans or not.')),
                ('allow_multiple', models.BooleanField(verbose_name='allow multiple', default=False, help_text='Designates whether this plan allow for multiple contractions.')),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('quantity', models.PositiveIntegerField(verbose_name='quantity', null=True, blank=True)),
                ('price', models.DecimalField(verbose_name='price', decimal_places=2, max_digits=12)),
                ('plan', models.ForeignKey(related_name='rates', verbose_name='plan', to='plans.Plan')),
                ('service', models.ForeignKey(related_name='rates', verbose_name='service', to='services.Service')),
            ],
        ),
        migrations.AddField(
            model_name='contractedplan',
            name='plan',
            field=models.ForeignKey(related_name='contracts', verbose_name='plan', to='plans.Plan'),
        ),
        migrations.AlterUniqueTogether(
            name='rate',
            unique_together=set([('service', 'plan', 'quantity')]),
        ),
    ]
