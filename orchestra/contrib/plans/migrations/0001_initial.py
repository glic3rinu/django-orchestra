# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import orchestra.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('services', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractedPlan',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='account', related_name='plans')),
            ],
            options={
                'verbose_name_plural': 'plans',
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(validators=[orchestra.core.validators.validate_name], unique=True, max_length=32, verbose_name='name')),
                ('verbose_name', models.CharField(max_length=128, verbose_name='verbose_name', blank=True)),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_default', models.BooleanField(default=False, help_text='Designates whether this plan is used by default or not.', verbose_name='default')),
                ('is_combinable', models.BooleanField(default=True, help_text='Designates whether this plan can be combined with other plans or not.', verbose_name='combinable')),
                ('allow_multiple', models.BooleanField(default=False, help_text='Designates whether this plan allow for multiple contractions.', verbose_name='allow multiple')),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(null=True, help_text='See rate algorihm help text.', verbose_name='quantity', blank=True)),
                ('price', models.DecimalField(max_digits=12, verbose_name='price', decimal_places=2)),
                ('plan', models.ForeignKey(to='plans.Plan', verbose_name='plan', related_name='rates')),
                ('service', models.ForeignKey(to='services.Service', verbose_name='service', related_name='rates')),
            ],
        ),
        migrations.AddField(
            model_name='contractedplan',
            name='plan',
            field=models.ForeignKey(to='plans.Plan', verbose_name='plan', related_name='contracts'),
        ),
        migrations.AlterUniqueTogether(
            name='rate',
            unique_together=set([('service', 'plan', 'quantity')]),
        ),
    ]
