# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('websites', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='website',
            name='domains',
            field=models.ManyToManyField(to='domains.Domain', related_name='websites', verbose_name='domains', blank=True),
        ),
        migrations.AlterField(
            model_name='websitedirective',
            name='name',
            field=models.CharField(choices=[(None, '-------'), ('HTTPD', [('redirect', 'Redirection'), ('proxy', 'Proxy'), ('error-document', 'ErrorDocumentRoot')]), ('SaaS', [('wordpress-saas', 'WordPress SaaS'), ('dokuwiki-saas', 'DokuWiki SaaS'), ('drupal-saas', 'Drupdal SaaS'), ('moodle-saas', 'Moodle SaaS')]), ('ModSecurity', [('sec-rule-remove', 'SecRuleRemoveById'), ('sec-engine', 'SecRuleEngine Off')]), ('SSL', [('ssl-ca', 'SSL CA'), ('ssl-cert', 'SSL cert'), ('ssl-key', 'SSL key')])], db_index=True, verbose_name='name', max_length=128),
        ),
    ]
