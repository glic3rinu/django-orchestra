# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0004_auto_20140911_1234'),
    ]

    operations = [
        migrations.RenameField(
            model_name='billsubline',
            old_name='bill_line',
            new_name='line',
        ),
    ]
