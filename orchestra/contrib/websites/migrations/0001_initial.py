# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orchestra.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('webapps', '0001_initial'),
        ('domains', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('path', models.CharField(verbose_name='path', blank=True, max_length=256, validators=[orchestra.core.validators.validate_url_path])),
                ('webapp', models.ForeignKey(to='webapps.WebApp', verbose_name='web application')),
            ],
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', max_length=128, validators=[orchestra.core.validators.validate_name])),
                ('protocol', models.CharField(default='http', verbose_name='protocol', max_length=16, help_text='Select the protocol(s) for this website<br><tt>HTTPS only</tt> performs a redirection from <tt>http</tt> to <tt>https</tt>.', choices=[('http', 'HTTP'), ('https', 'HTTPS'), ('http/https', 'HTTP and HTTPS'), ('https-only', 'HTTPS only')])),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='websites', verbose_name='Account')),
                ('contents', models.ManyToManyField(to='webapps.WebApp', through='websites.Content')),
                ('domains', models.ManyToManyField(to='domains.Domain', verbose_name='domains', related_name='websites')),
            ],
        ),
        migrations.CreateModel(
            name='WebsiteDirective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', max_length=128, choices=[(None, '-------'), ('SaaS', [('wordpress-saas', 'WordPress SaaS'), ('dokuwiki-saas', 'DokuWiki SaaS'), ('drupal-saas', 'Drupdal SaaS')]), ('ModSecurity', [('sec-rule-remove', 'SecRuleRemoveById'), ('sec-engine', 'SecRuleEngine Off')]), ('HTTPD', [('redirect', 'Redirection'), ('proxy', 'Proxy'), ('error-document', 'ErrorDocumentRoot')]), ('SSL', [('ssl-ca', 'SSL CA'), ('ssl-cert', 'SSL cert'), ('ssl-key', 'SSL key')])])),
                ('value', models.CharField(verbose_name='value', max_length=256)),
                ('website', models.ForeignKey(to='websites.Website', related_name='directives', verbose_name='web site')),
            ],
        ),
        migrations.AddField(
            model_name='content',
            name='website',
            field=models.ForeignKey(to='websites.Website', verbose_name='web site'),
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
