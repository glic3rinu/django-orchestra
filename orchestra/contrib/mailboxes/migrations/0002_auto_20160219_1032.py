# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('mailboxes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailbox',
            name='filtering',
            field=models.CharField(max_length=16, choices=[('CUSTOM', 'Custom filtering'), ('DISABLE', 'Disable'), ('REDIRECT', 'Archive spam (Score&ge;8)'), ('REDIRECT5', 'Archive spam (Score&ge;5)'), ('REJECT', 'Reject spam (Score&ge;8)'), ('REJECT5', 'Reject spam (Score&ge;5)')], default='REDIRECT'),
        ),
        migrations.AlterField(
            model_name='mailbox',
            name='name',
            field=models.CharField(max_length=64, db_index=True, unique=True, help_text='Required. 32 characters or fewer. Letters, digits and ./-/_ only.', validators=[django.core.validators.RegexValidator('^[\\w.-]+$', 'Enter a valid mailbox name.')], verbose_name='name'),
        ),
    ]
