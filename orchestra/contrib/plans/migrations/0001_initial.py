# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractedPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='plans', verbose_name='account')),
            ],
            options={
                'verbose_name_plural': 'plans',
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(validators=[orchestra.core.validators.validate_name], verbose_name='name', unique=True, max_length=32)),
                ('verbose_name', models.CharField(blank=True, verbose_name='verbose_name', max_length=128)),
                ('is_active', models.BooleanField(help_text='Designates whether this account should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active', default=True)),
                ('is_default', models.BooleanField(help_text='Designates whether this plan is used by default or not.', verbose_name='default', default=False)),
                ('is_combinable', models.BooleanField(help_text='Designates whether this plan can be combined with other plans or not.', verbose_name='combinable', default=True)),
                ('allow_multiple', models.BooleanField(help_text='Designates whether this plan allow for multiple contractions.', verbose_name='allow multiple', default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(help_text='See rate algorihm help text.', blank=True, verbose_name='quantity', null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='price')),
                ('plan', models.ForeignKey(to='plans.Plan', related_name='rates', verbose_name='plan')),
                ('service', models.ForeignKey(to='services.Service', related_name='rates', verbose_name='service')),
            ],
        ),
        migrations.AddField(
            model_name='contractedplan',
            name='plan',
            field=models.ForeignKey(to='plans.Plan', related_name='contracts', verbose_name='plan'),
        ),
        migrations.AlterUniqueTogether(
            name='rate',
            unique_together=set([('service', 'plan', 'quantity')]),
        ),
    ]
