# -*- coding: utf-8 -*-

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('webapps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webapp',
            name='data',
            field=jsonfield.fields.JSONField(default={}, help_text='Extra information dependent of each service.', verbose_name='data'),
            preserve_default=False,
        ),
    ]
