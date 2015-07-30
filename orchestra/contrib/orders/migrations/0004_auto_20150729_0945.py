# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_content_object_repr'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='billed_metric',
            field=models.DecimalField(verbose_name='billed metric', max_digits=16, decimal_places=2, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='content_object_repr',
            field=models.CharField(verbose_name='content object representation', max_length=256, editable=False),
        ),
    ]
