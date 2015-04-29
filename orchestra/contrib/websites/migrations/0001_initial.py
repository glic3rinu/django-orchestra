# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import orchestra.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('domains', '0001_initial'),
        ('webapps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('path', models.CharField(validators=[orchestra.core.validators.validate_url_path], verbose_name='path', max_length=256, blank=True)),
                ('webapp', models.ForeignKey(verbose_name='web application', to='webapps.WebApp')),
            ],
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(validators=[orchestra.core.validators.validate_name], verbose_name='name', max_length=128)),
                ('protocol', models.CharField(verbose_name='protocol', default='http', choices=[('http', 'HTTP'), ('https', 'HTTPS'), ('http/https', 'HTTP and HTTPS'), ('https-only', 'HTTPS only')], help_text='Select the protocol(s) for this website<br><tt>HTTPS only</tt> performs a redirection from <tt>http</tt> to <tt>https</tt>.', max_length=16)),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
                ('account', models.ForeignKey(related_name='websites', verbose_name='Account', to=settings.AUTH_USER_MODEL)),
                ('contents', models.ManyToManyField(through='websites.Content', to='webapps.WebApp')),
                ('domains', models.ManyToManyField(verbose_name='domains', related_name='websites', to='domains.Domain')),
            ],
        ),
        migrations.CreateModel(
            name='WebsiteDirective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='name', choices=[(None, '-------'), ('SSL', [('ssl-ca', 'SSL CA'), ('ssl-cert', 'SSL cert'), ('ssl-key', 'SSL key')]), ('HTTPD', [('redirect', 'Redirection'), ('proxy', 'Proxy'), ('error-document', 'ErrorDocumentRoot')]), ('ModSecurity', [('sec-rule-remove', 'SecRuleRemoveById'), ('sec-engine', 'SecRuleEngine Off')]), ('SaaS', [('wordpress-saas', 'WordPress SaaS'), ('dokuwiki-saas', 'DokuWiki SaaS'), ('drupal-saas', 'Drupdal SaaS')])], max_length=128)),
                ('value', models.CharField(verbose_name='value', max_length=256)),
                ('website', models.ForeignKey(related_name='directives', verbose_name='web site', to='websites.Website')),
            ],
        ),
        migrations.AddField(
            model_name='content',
            name='website',
            field=models.ForeignKey(verbose_name='web site', to='websites.Website'),
        ),
        migrations.AlterUniqueTogether(
            name='website',
            unique_together=set([('name', 'account')]),
        ),
        migrations.AlterUniqueTogether(
            name='content',
            unique_together=set([('website', 'path')]),
        ),
    ]
