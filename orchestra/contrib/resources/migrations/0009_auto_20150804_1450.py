# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0008_monitordata_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcedata',
            name='allocated',
            field=models.PositiveIntegerField(verbose_name='allocated', null=True, blank=True),
        ),
    ]
