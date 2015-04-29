# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('number', models.CharField(unique=True, verbose_name='number', blank=True, max_length=16)),
                ('type', models.CharField(verbose_name='type', choices=[('INVOICE', 'Invoice'), ('AMENDMENTINVOICE', 'Amendment invoice'), ('FEE', 'Fee'), ('AMENDMENTFEE', 'Amendment Fee'), ('PROFORMA', 'Pro forma')], max_length=16)),
                ('created_on', models.DateField(auto_now_add=True, verbose_name='created on')),
                ('closed_on', models.DateField(verbose_name='closed on', null=True, blank=True)),
                ('is_open', models.BooleanField(default=True, verbose_name='open')),
                ('is_sent', models.BooleanField(default=False, verbose_name='sent')),
                ('due_on', models.DateField(verbose_name='due on', null=True, blank=True)),
                ('updated_on', models.DateField(verbose_name='updated on', auto_now=True)),
                ('total', models.DecimalField(default=0, decimal_places=2, max_digits=12)),
                ('comments', models.TextField(verbose_name='comments', blank=True)),
                ('html', models.TextField(verbose_name='HTML', blank=True)),
                ('account', models.ForeignKey(related_name='bill', to=settings.AUTH_USER_MODEL, verbose_name='account')),
            ],
            options={
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='BillContact',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', blank=True, max_length=256, help_text='Account full name will be used when left blank.')),
                ('address', models.TextField(verbose_name='address')),
                ('city', models.CharField(default='Barcelona', verbose_name='city', max_length=128)),
                ('zipcode', models.CharField(verbose_name='zip code', validators=[django.core.validators.RegexValidator('^[0-9A-Z]{3,10}$', 'Enter a valid zipcode.')], max_length=10)),
                ('country', models.CharField(default='ES', verbose_name='country', choices=[('PR', 'Puerto Rico'), ('BV', 'Bouvet Island'), ('BT', 'Bhutan'), ('MY', 'Malaysia'), ('AQ', 'Antarctica'), ('MT', 'Malta'), ('BE', 'Belgium'), ('SM', 'San Marino'), ('AZ', 'Azerbaijan'), ('CA', 'Canada'), ('HR', 'Croatia'), ('GH', 'Ghana'), ('MZ', 'Mozambique'), ('PA', 'Panama'), ('GR', 'Greece'), ('AE', 'United Arab Emirates'), ('CK', 'Cook Islands'), ('SK', 'Slovakia'), ('PN', 'Pitcairn'), ('ZA', 'South Africa'), ('AU', 'Australia'), ('BF', 'Burkina Faso'), ('FI', 'Finland'), ('MC', 'Monaco'), ('RE', 'Réunion'), ('TV', 'Tuvalu'), ('HN', 'Honduras'), ('IL', 'Israel'), ('SV', 'El Salvador'), ('VN', 'Viet Nam'), ('MV', 'Maldives'), ('BA', 'Bosnia and Herzegovina'), ('UA', 'Ukraine'), ('BW', 'Botswana'), ('UZ', 'Uzbekistan'), ('ID', 'Indonesia'), ('LY', 'Libya'), ('MM', 'Myanmar'), ('TZ', 'Tanzania, United Republic of'), ('GL', 'Greenland'), ('LV', 'Latvia'), ('DZ', 'Algeria'), ('AO', 'Angola'), ('GE', 'Georgia'), ('SO', 'Somalia'), ('CX', 'Christmas Island'), ('NP', 'Nepal'), ('AI', 'Anguilla'), ('GP', 'Guadeloupe'), ('UY', 'Uruguay'), ('LC', 'Saint Lucia'), ('EH', 'Western Sahara'), ('IO', 'British Indian Ocean Territory'), ('TH', 'Thailand'), ('AR', 'Argentina'), ('PY', 'Paraguay'), ('AW', 'Aruba'), ('IE', 'Ireland'), ('CF', 'Central African Republic'), ('TW', 'Taiwan (Province of China)'), ('KZ', 'Kazakhstan'), ('TJ', 'Tajikistan'), ('RW', 'Rwanda'), ('SR', 'Suriname'), ('AT', 'Austria'), ('GN', 'Guinea'), ('SS', 'South Sudan'), ('IT', 'Italy'), ('BO', 'Bolivia (Plurinational State of)'), ('GD', 'Grenada'), ('KE', 'Kenya'), ('GS', 'South Georgia and the South Sandwich Islands'), ('TG', 'Togo'), ('CY', 'Cyprus'), ('TT', 'Trinidad and Tobago'), ('CM', 'Cameroon'), ('QA', 'Qatar'), ('GM', 'Gambia'), ('WS', 'Samoa'), ('DJ', 'Djibouti'), ('PL', 'Poland'), ('CV', 'Cabo Verde'), ('PE', 'Peru'), ('TN', 'Tunisia'), ('HT', 'Haiti'), ('AF', 'Afghanistan'), ('YT', 'Mayotte'), ('NR', 'Nauru'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('IR', 'Iran (Islamic Republic of)'), ('EE', 'Estonia'), ('ER', 'Eritrea'), ('RU', 'Russian Federation'), ('LB', 'Lebanon'), ('CU', 'Cuba'), ('CZ', 'Czech Republic'), ('AX', 'Åland Islands'), ('CD', 'Congo (the Democratic Republic of the)'), ('HK', 'Hong Kong'), ('PS', 'Palestine, State of'), ('FK', 'Falkland Islands  [Malvinas]'), ('MR', 'Mauritania'), ('MG', 'Madagascar'), ('MH', 'Marshall Islands'), ('LK', 'Sri Lanka'), ('NA', 'Namibia'), ('SI', 'Slovenia'), ('BY', 'Belarus'), ('MX', 'Mexico'), ('ZW', 'Zimbabwe'), ('CI', "Côte d'Ivoire"), ('GU', 'Guam'), ('PW', 'Palau'), ('SC', 'Seychelles'), ('GT', 'Guatemala'), ('CL', 'Chile'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'), ('BH', 'Bahrain'), ('SB', 'Solomon Islands'), ('KM', 'Comoros'), ('MF', 'Saint Martin (French part)'), ('FO', 'Faroe Islands'), ('BD', 'Bangladesh'), ('AM', 'Armenia'), ('BJ', 'Benin'), ('SA', 'Saudi Arabia'), ('NU', 'Niue'), ('VI', 'Virgin Islands (U.S.)'), ('CN', 'China'), ('EC', 'Ecuador'), ('CC', 'Cocos (Keeling) Islands'), ('BS', 'Bahamas'), ('JM', 'Jamaica'), ('RO', 'Romania'), ('KI', 'Kiribati'), ('GY', 'Guyana'), ('TL', 'Timor-Leste'), ('AS', 'American Samoa'), ('VE', 'Venezuela (Bolivarian Republic of)'), ('BN', 'Brunei Darussalam'), ('ET', 'Ethiopia'), ('FJ', 'Fiji'), ('BG', 'Bulgaria'), ('VG', 'Virgin Islands (British)'), ('AD', 'Andorra'), ('KN', 'Saint Kitts and Nevis'), ('MA', 'Morocco'), ('MU', 'Mauritius'), ('DK', 'Denmark'), ('TO', 'Tonga'), ('CO', 'Colombia'), ('GA', 'Gabon'), ('MK', 'Macedonia (the former Yugoslav Republic of)'), ('MD', 'Moldova (the Republic of)'), ('VA', 'Holy See'), ('KY', 'Cayman Islands'), ('LU', 'Luxembourg'), ('AL', 'Albania'), ('LI', 'Liechtenstein'), ('KP', "Korea (the Democratic People's Republic of)"), ('BZ', 'Belize'), ('ME', 'Montenegro'), ('NC', 'New Caledonia'), ('VC', 'Saint Vincent and the Grenadines'), ('UM', 'United States Minor Outlying Islands'), ('IQ', 'Iraq'), ('GB', 'United Kingdom of Great Britain and Northern Ireland'), ('KW', 'Kuwait'), ('MS', 'Montserrat'), ('SD', 'Sudan'), ('JP', 'Japan'), ('DE', 'Germany'), ('SN', 'Senegal'), ('PK', 'Pakistan'), ('MO', 'Macao'), ('RS', 'Serbia'), ('KR', 'Korea (the Republic of)'), ('BL', 'Saint Barthélemy'), ('MP', 'Northern Mariana Islands'), ('AG', 'Antigua and Barbuda'), ('FM', 'Micronesia (Federated States of)'), ('HM', 'Heard Island and McDonald Islands'), ('BR', 'Brazil'), ('PF', 'French Polynesia'), ('MQ', 'Martinique'), ('VU', 'Vanuatu'), ('LT', 'Lithuania'), ('ES', 'Spain'), ('ML', 'Mali'), ('NE', 'Niger'), ('EG', 'Egypt'), ('WF', 'Wallis and Futuna'), ('ZM', 'Zambia'), ('US', 'United States of America'), ('DO', 'Dominican Republic'), ('NO', 'Norway'), ('UG', 'Uganda'), ('GQ', 'Equatorial Guinea'), ('GW', 'Guinea-Bissau'), ('JE', 'Jersey'), ('HU', 'Hungary'), ('BQ', 'Bonaire, Sint Eustatius and Saba'), ('JO', 'Jordan'), ('ST', 'Sao Tome and Principe'), ('SJ', 'Svalbard and Jan Mayen'), ('MN', 'Mongolia'), ('BB', 'Barbados'), ('CH', 'Switzerland'), ('KG', 'Kyrgyzstan'), ('PG', 'Papua New Guinea'), ('NG', 'Nigeria'), ('GF', 'French Guiana'), ('CR', 'Costa Rica'), ('LA', "Lao People's Democratic Republic"), ('CG', 'Congo'), ('NI', 'Nicaragua'), ('TK', 'Tokelau'), ('SE', 'Sweden'), ('NF', 'Norfolk Island'), ('PT', 'Portugal'), ('FR', 'France'), ('SZ', 'Swaziland'), ('YE', 'Yemen'), ('NL', 'Netherlands'), ('GI', 'Gibraltar'), ('TR', 'Turkey'), ('OM', 'Oman'), ('TF', 'French Southern Territories'), ('PM', 'Saint Pierre and Miquelon'), ('TC', 'Turks and Caicos Islands'), ('SL', 'Sierra Leone'), ('SX', 'Sint Maarten (Dutch part)'), ('DM', 'Dominica'), ('KH', 'Cambodia'), ('SG', 'Singapore'), ('BM', 'Bermuda'), ('CW', 'Curaçao'), ('GG', 'Guernsey'), ('TD', 'Chad'), ('IN', 'India'), ('BI', 'Burundi'), ('TM', 'Turkmenistan'), ('IS', 'Iceland'), ('MW', 'Malawi'), ('SY', 'Syrian Arab Republic'), ('NZ', 'New Zealand'), ('IM', 'Isle of Man'), ('PH', 'Philippines')], max_length=20)),
                ('vat', models.CharField(verbose_name='VAT number', max_length=64)),
                ('account', models.OneToOneField(related_name='billcontact', to=settings.AUTH_USER_MODEL, verbose_name='account')),
            ],
        ),
        migrations.CreateModel(
            name='BillLine',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='description', max_length=256)),
                ('rate', models.DecimalField(decimal_places=2, verbose_name='rate', null=True, blank=True, max_digits=12)),
                ('quantity', models.DecimalField(verbose_name='quantity', decimal_places=2, max_digits=12)),
                ('verbose_quantity', models.CharField(verbose_name='Verbose quantity', max_length=16)),
                ('subtotal', models.DecimalField(verbose_name='subtotal', decimal_places=2, max_digits=12)),
                ('tax', models.DecimalField(verbose_name='tax', decimal_places=2, max_digits=4)),
                ('start_on', models.DateField(verbose_name='start')),
                ('end_on', models.DateField(verbose_name='end', null=True)),
                ('order_billed_on', models.DateField(verbose_name='order billed', null=True, blank=True)),
                ('order_billed_until', models.DateField(verbose_name='order billed until', null=True, blank=True)),
                ('created_on', models.DateField(auto_now_add=True, verbose_name='created')),
                ('amended_line', models.ForeignKey(blank=True, to='bills.BillLine', verbose_name='amended line', null=True, related_name='amendment_lines')),
                ('bill', models.ForeignKey(related_name='lines', to='bills.Bill', verbose_name='bill')),
                ('order', models.ForeignKey(blank=True, to='orders.Order', null=True, on_delete=django.db.models.deletion.SET_NULL, help_text='Informative link back to the order')),
            ],
        ),
        migrations.CreateModel(
            name='BillSubline',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='description', max_length=256)),
                ('total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('type', models.CharField(default='OTHER', verbose_name='type', choices=[('VOLUME', 'Volume'), ('COMPENSATION', 'Compensation'), ('OTHER', 'Other')], max_length=16)),
                ('line', models.ForeignKey(related_name='sublines', to='bills.BillLine', verbose_name='bill line')),
            ],
        ),
        migrations.CreateModel(
            name='AmendmentFee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='AmendmentInvoice',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
        migrations.CreateModel(
            name='ProForma',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('bills.bill',),
        ),
    ]
