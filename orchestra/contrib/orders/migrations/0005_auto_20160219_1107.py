# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20150729_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='billed_metric',
            field=models.DecimalField(decimal_places=2, null=True, verbose_name='billed metric', blank=True, max_digits=16),
        ),
        migrations.AlterField(
            model_name='order',
            name='content_object_repr',
            field=models.CharField(max_length=256, verbose_name='content object representation', help_text='Used for searches.', editable=False),
        ),
        migrations.AlterIndexTogether(
            name='order',
            index_together=set([('content_type', 'object_id')]),
        ),
    ]
