# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0007_auto_20140918_1454'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bill',
            options={'get_latest_by': 'id'},
        ),
    ]
