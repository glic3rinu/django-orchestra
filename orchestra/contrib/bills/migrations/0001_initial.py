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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('number', models.CharField(max_length=16, verbose_name='number', blank=True, unique=True)),
                ('type', models.CharField(verbose_name='type', choices=[('INVOICE', 'Invoice'), ('AMENDMENTINVOICE', 'Amendment invoice'), ('FEE', 'Fee'), ('AMENDMENTFEE', 'Amendment Fee'), ('PROFORMA', 'Pro forma')], max_length=16)),
                ('created_on', models.DateField(auto_now_add=True, verbose_name='created on')),
                ('closed_on', models.DateField(null=True, verbose_name='closed on', blank=True)),
                ('is_open', models.BooleanField(verbose_name='open', default=True)),
                ('is_sent', models.BooleanField(verbose_name='sent', default=False)),
                ('due_on', models.DateField(null=True, verbose_name='due on', blank=True)),
                ('updated_on', models.DateField(verbose_name='updated on', auto_now=True)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='name', help_text='Account full name will be used when left blank.', blank=True, max_length=256)),
                ('address', models.TextField(verbose_name='address')),
                ('city', models.CharField(verbose_name='city', default='Barcelona', max_length=128)),
                ('zipcode', models.CharField(verbose_name='zip code', max_length=10, validators=[django.core.validators.RegexValidator('^[0-9A-Z]{3,10}$', 'Enter a valid zipcode.')])),
                ('country', models.CharField(verbose_name='country', default='ES', choices=[('BZ', 'Belize'), ('MZ', 'Mozambique'), ('ER', 'Eritrea'), ('AL', 'Albania'), ('CU', 'Cuba'), ('AM', 'Armenia'), ('ZW', 'Zimbabwe'), ('RU', 'Russian Federation'), ('PR', 'Puerto Rico'), ('MM', 'Myanmar'), ('UG', 'Uganda'), ('IQ', 'Iraq'), ('RS', 'Serbia'), ('KM', 'Comoros'), ('MY', 'Malaysia'), ('PH', 'Philippines'), ('TJ', 'Tajikistan'), ('GA', 'Gabon'), ('CL', 'Chile'), ('AG', 'Antigua and Barbuda'), ('DM', 'Dominica'), ('TC', 'Turks and Caicos Islands'), ('KI', 'Kiribati'), ('KZ', 'Kazakhstan'), ('ME', 'Montenegro'), ('BD', 'Bangladesh'), ('KW', 'Kuwait'), ('LI', 'Liechtenstein'), ('PS', 'Palestine, State of'), ('BI', 'Burundi'), ('TR', 'Turkey'), ('GF', 'French Guiana'), ('CD', 'Congo (the Democratic Republic of the)'), ('AU', 'Australia'), ('BR', 'Brazil'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'), ('PM', 'Saint Pierre and Miquelon'), ('NG', 'Nigeria'), ('TL', 'Timor-Leste'), ('LR', 'Liberia'), ('AF', 'Afghanistan'), ('HM', 'Heard Island and McDonald Islands'), ('SI', 'Slovenia'), ('MP', 'Northern Mariana Islands'), ('SN', 'Senegal'), ('PF', 'French Polynesia'), ('NZ', 'New Zealand'), ('TD', 'Chad'), ('PW', 'Palau'), ('FJ', 'Fiji'), ('PE', 'Peru'), ('CR', 'Costa Rica'), ('GD', 'Grenada'), ('CZ', 'Czech Republic'), ('YT', 'Mayotte'), ('AW', 'Aruba'), ('SK', 'Slovakia'), ('YE', 'Yemen'), ('BW', 'Botswana'), ('MK', 'Macedonia (the former Yugoslav Republic of)'), ('KR', 'Korea (the Republic of)'), ('VU', 'Vanuatu'), ('BV', 'Bouvet Island'), ('CM', 'Cameroon'), ('ZM', 'Zambia'), ('LB', 'Lebanon'), ('SE', 'Sweden'), ('NE', 'Niger'), ('CG', 'Congo'), ('IN', 'India'), ('IL', 'Israel'), ('TT', 'Trinidad and Tobago'), ('EE', 'Estonia'), ('MX', 'Mexico'), ('TW', 'Taiwan (Province of China)'), ('AI', 'Anguilla'), ('OM', 'Oman'), ('ML', 'Mali'), ('NP', 'Nepal'), ('VE', 'Venezuela (Bolivarian Republic of)'), ('BJ', 'Benin'), ('MT', 'Malta'), ('AZ', 'Azerbaijan'), ('UA', 'Ukraine'), ('JO', 'Jordan'), ('TZ', 'Tanzania, United Republic of'), ('AX', 'Åland Islands'), ('PT', 'Portugal'), ('NU', 'Niue'), ('VG', 'Virgin Islands (British)'), ('TH', 'Thailand'), ('CY', 'Cyprus'), ('AR', 'Argentina'), ('CO', 'Colombia'), ('IE', 'Ireland'), ('LA', "Lao People's Democratic Republic"), ('MS', 'Montserrat'), ('AD', 'Andorra'), ('SC', 'Seychelles'), ('PN', 'Pitcairn'), ('TN', 'Tunisia'), ('GI', 'Gibraltar'), ('GU', 'Guam'), ('SB', 'Solomon Islands'), ('MC', 'Monaco'), ('CN', 'China'), ('ZA', 'South Africa'), ('KE', 'Kenya'), ('IT', 'Italy'), ('HR', 'Croatia'), ('GY', 'Guyana'), ('BG', 'Bulgaria'), ('HU', 'Hungary'), ('CC', 'Cocos (Keeling) Islands'), ('MR', 'Mauritania'), ('SY', 'Syrian Arab Republic'), ('CF', 'Central African Republic'), ('KN', 'Saint Kitts and Nevis'), ('SX', 'Sint Maarten (Dutch part)'), ('SJ', 'Svalbard and Jan Mayen'), ('GH', 'Ghana'), ('VI', 'Virgin Islands (U.S.)'), ('HN', 'Honduras'), ('KG', 'Kyrgyzstan'), ('GQ', 'Equatorial Guinea'), ('IS', 'Iceland'), ('JP', 'Japan'), ('BL', 'Saint Barthélemy'), ('GB', 'United Kingdom of Great Britain and Northern Ireland'), ('TF', 'French Southern Territories'), ('IO', 'British Indian Ocean Territory'), ('PY', 'Paraguay'), ('RE', 'Réunion'), ('GG', 'Guernsey'), ('RW', 'Rwanda'), ('FI', 'Finland'), ('CA', 'Canada'), ('IM', 'Isle of Man'), ('ES', 'Spain'), ('HT', 'Haiti'), ('VN', 'Viet Nam'), ('WF', 'Wallis and Futuna'), ('GL', 'Greenland'), ('GP', 'Guadeloupe'), ('EG', 'Egypt'), ('BA', 'Bosnia and Herzegovina'), ('IR', 'Iran (Islamic Republic of)'), ('HK', 'Hong Kong'), ('TG', 'Togo'), ('PG', 'Papua New Guinea'), ('SS', 'South Sudan'), ('AS', 'American Samoa'), ('LC', 'Saint Lucia'), ('LU', 'Luxembourg'), ('SO', 'Somalia'), ('JE', 'Jersey'), ('GR', 'Greece'), ('EH', 'Western Sahara'), ('MU', 'Mauritius'), ('CI', "Côte d'Ivoire"), ('BH', 'Bahrain'), ('BF', 'Burkina Faso'), ('TM', 'Turkmenistan'), ('PK', 'Pakistan'), ('KY', 'Cayman Islands'), ('GE', 'Georgia'), ('VC', 'Saint Vincent and the Grenadines'), ('FR', 'France'), ('AQ', 'Antarctica'), ('LT', 'Lithuania'), ('BY', 'Belarus'), ('DK', 'Denmark'), ('RO', 'Romania'), ('GT', 'Guatemala'), ('SM', 'San Marino'), ('CW', 'Curaçao'), ('MO', 'Macao'), ('MV', 'Maldives'), ('DE', 'Germany'), ('UZ', 'Uzbekistan'), ('TK', 'Tokelau'), ('FO', 'Faroe Islands'), ('NI', 'Nicaragua'), ('MF', 'Saint Martin (French part)'), ('UM', 'United States Minor Outlying Islands'), ('LK', 'Sri Lanka'), ('NL', 'Netherlands'), ('NR', 'Nauru'), ('BO', 'Bolivia (Plurinational State of)'), ('GN', 'Guinea'), ('AE', 'United Arab Emirates'), ('BE', 'Belgium'), ('NA', 'Namibia'), ('BN', 'Brunei Darussalam'), ('MW', 'Malawi'), ('BQ', 'Bonaire, Sint Eustatius and Saba'), ('ET', 'Ethiopia'), ('CK', 'Cook Islands'), ('BT', 'Bhutan'), ('DO', 'Dominican Republic'), ('DZ', 'Algeria'), ('MQ', 'Martinique'), ('DJ', 'Djibouti'), ('ST', 'Sao Tome and Principe'), ('KH', 'Cambodia'), ('CX', 'Christmas Island'), ('CV', 'Cabo Verde'), ('QA', 'Qatar'), ('GS', 'South Georgia and the South Sandwich Islands'), ('FK', 'Falkland Islands  [Malvinas]'), ('BS', 'Bahamas'), ('GW', 'Guinea-Bissau'), ('MA', 'Morocco'), ('PL', 'Poland'), ('ID', 'Indonesia'), ('GM', 'Gambia'), ('US', 'United States of America'), ('MN', 'Mongolia'), ('CH', 'Switzerland'), ('MH', 'Marshall Islands'), ('SR', 'Suriname'), ('EC', 'Ecuador'), ('SA', 'Saudi Arabia'), ('JM', 'Jamaica'), ('MG', 'Madagascar'), ('FM', 'Micronesia (Federated States of)'), ('AO', 'Angola'), ('SL', 'Sierra Leone'), ('KP', "Korea (the Democratic People's Republic of)"), ('BB', 'Barbados'), ('NC', 'New Caledonia'), ('TV', 'Tuvalu'), ('BM', 'Bermuda'), ('LS', 'Lesotho'), ('AT', 'Austria'), ('UY', 'Uruguay'), ('SG', 'Singapore'), ('TO', 'Tonga'), ('NF', 'Norfolk Island'), ('MD', 'Moldova (the Republic of)'), ('SZ', 'Swaziland'), ('WS', 'Samoa'), ('PA', 'Panama'), ('SD', 'Sudan'), ('NO', 'Norway'), ('LY', 'Libya'), ('LV', 'Latvia'), ('VA', 'Holy See'), ('SV', 'El Salvador')], max_length=20)),
                ('vat', models.CharField(verbose_name='VAT number', max_length=64)),
                ('account', models.OneToOneField(related_name='billcontact', to=settings.AUTH_USER_MODEL, verbose_name='account')),
            ],
        ),
        migrations.CreateModel(
            name='BillLine',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('description', models.CharField(verbose_name='description', max_length=256)),
                ('rate', models.DecimalField(null=True, verbose_name='rate', decimal_places=2, blank=True, max_digits=12)),
                ('quantity', models.DecimalField(verbose_name='quantity', decimal_places=2, max_digits=12)),
                ('verbose_quantity', models.CharField(verbose_name='Verbose quantity', max_length=16)),
                ('subtotal', models.DecimalField(verbose_name='subtotal', decimal_places=2, max_digits=12)),
                ('tax', models.DecimalField(verbose_name='tax', decimal_places=2, max_digits=4)),
                ('start_on', models.DateField(verbose_name='start')),
                ('end_on', models.DateField(null=True, verbose_name='end')),
                ('order_billed_on', models.DateField(null=True, verbose_name='order billed', blank=True)),
                ('order_billed_until', models.DateField(null=True, verbose_name='order billed until', blank=True)),
                ('created_on', models.DateField(auto_now_add=True, verbose_name='created')),
                ('amended_line', models.ForeignKey(related_name='amendment_lines', blank=True, to='bills.BillLine', null=True, verbose_name='amended line')),
                ('bill', models.ForeignKey(related_name='lines', to='bills.Bill', verbose_name='bill')),
                ('order', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True, to='orders.Order', help_text='Informative link back to the order')),
            ],
        ),
        migrations.CreateModel(
            name='BillSubline',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('description', models.CharField(verbose_name='description', max_length=256)),
                ('total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('type', models.CharField(verbose_name='type', default='OTHER', choices=[('VOLUME', 'Volume'), ('COMPENSATION', 'Compensation'), ('OTHER', 'Other')], max_length=16)),
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
