# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0011_auto_20140926_1334'),
    ]

    operations = [
        migrations.RenameField(
            model_name='billline',
            old_name='order_id',
            new_name='order',
        ),
    ]
