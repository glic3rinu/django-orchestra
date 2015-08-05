# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0007_auto_20150723_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitordata',
            name='state',
            field=models.DecimalField(verbose_name='state', null=True, max_digits=16, help_text='Optional field used to store current state needed for diff-based monitoring.', decimal_places=2),
        ),
    ]
