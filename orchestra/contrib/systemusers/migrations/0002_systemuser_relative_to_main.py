# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('systemusers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemuser',
            name='relative_to_main',
            field=models.BooleanField(default=False, choices=[(True, b'Hola'), (False, b'adeu')]),
            preserve_default=True,
        ),
    ]
