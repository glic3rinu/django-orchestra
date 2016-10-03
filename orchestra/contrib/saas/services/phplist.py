from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.mailboxes.models import Mailbox
from orchestra.forms.widgets import SpanWidget

from .. import settings
from ..forms import SaaSPasswordForm
from .options import DBSoftwareService


class PHPListForm(SaaSPasswordForm):
    admin_username = forms.CharField(label=_("Admin username"), required=False,
        widget=SpanWidget(display='admin'))
    database = forms.CharField(label=_("Database"), required=False,
        help_text=_("Database dedicated to this phpList instance."),
        widget=SpanWidget(display=settings.SAAS_PHPLIST_DB_NAME.replace(
            '%(', '&lt;').replace(')s', '&gt;')))
    mailbox = forms.CharField(label=_("Bounces mailbox"), required=False,
        help_text=_("Dedicated mailbox used for reciving bounces."),
        widget=SpanWidget(display=settings.SAAS_PHPLIST_BOUNCES_MAILBOX_NAME.replace(
            '%(', '&lt;').replace(')s', '&gt;')))
    
    def __init__(self, *args, **kwargs):
        super(PHPListForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = _("Site name")
        context = {
            'site_name': '&lt;site_name&gt;',
            'name': '&lt;site_name&gt;',
        }
        domain = self.plugin.site_domain % context
        help_text = _("Admin URL http://{}/admin/").format(domain)
        self.fields['site_url'].help_text = help_text
        validator = validators.MaxLengthValidator(settings.SAAS_PHPLIST_NAME_MAX_LENGTH)
        self.fields['name'].validators.append(validator)


class PHPListChangeForm(PHPListForm):
    def __init__(self, *args, **kwargs):
        super(PHPListChangeForm, self).__init__(*args, **kwargs)
        site_domain = self.instance.get_site_domain()
        admin_url = "http://%s/admin/" % site_domain
        help_text = _("Admin URL <a href={0}>{0}</a>").format(admin_url)
        self.fields['site_url'].help_text = help_text
        # DB link
        db = self.instance.database
        db_url = reverse('admin:databases_database_change', args=(db.pk,))
        db_link = mark_safe('<a href="%s">%s</a>' % (db_url, db.name))
        self.fields['database'].widget = SpanWidget(original=db.name, display=db_link)
        # Mailbox link
        mailbox_id = self.instance.data.get('mailbox_id')
        if mailbox_id:
            try:
                mailbox = Mailbox.objects.get(id=mailbox_id)
            except Mailbox.DoesNotExist:
                pass
            else:
                mailbox_url = reverse('admin:mailboxes_mailbox_change', args=(mailbox.pk,))
                mailbox_link = mark_safe('<a href="%s">%s</a>' % (mailbox_url, mailbox.name))
                self.fields['mailbox'].widget = SpanWidget(
                    original=mailbox.name, display=mailbox_link)


class PHPListService(DBSoftwareService):
    name = 'phplist'
    verbose_name = "phpList"
    form = PHPListForm
    change_form = PHPListChangeForm
    icon = 'orchestra/icons/apps/Phplist.png'
    site_domain = settings.SAAS_PHPLIST_DOMAIN
    allow_custom_url = settings.SAAS_PHPLIST_ALLOW_CUSTOM_URL
    db_name = settings.SAAS_PHPLIST_DB_NAME
    db_user = settings.SAAS_PHPLIST_DB_USER
    
    def get_mailbox_name(self):
        context = {
            'name': self.instance.name,
            'site_name': self.instance.name,
        }
        return settings.SAAS_PHPLIST_BOUNCES_MAILBOX_NAME % context
    
    def validate(self):
        super(PHPListService, self).validate()
        create = not self.instance.pk
        if create:
            account = self.get_account()
            # Validate mailbox
            mailbox = Mailbox(name=self.get_mailbox_name(), account=account)
            try:
                mailbox.full_clean()
            except ValidationError as e:
                raise ValidationError({
                    'name': e.messages,
                })
    
    def save(self):
        super(PHPListService, self).save()
        account = self.get_account()
        # Mailbox
        mailbox_name = self.get_mailbox_name()
        mailbox, mb_created = account.mailboxes.get_or_create(name=mailbox_name)
        if mb_created:
            mailbox.set_password(settings.SAAS_PHPLIST_BOUNCES_MAILBOX_PASSWORD)
            mailbox.save(update_fields=('password',))
            self.instance.data.update({
                'mailbox_id': mailbox.pk,
                'mailbox_name': mailbox_name,
            })
    
    def delete(self):
        super(PHPListService, self).save()
        account = self.get_account()
        # delete Mailbox (database will be deleted by ORM's cascade behaviour
        mailbox_name = self.instance.data.get('mailbox_name') or self.get_mailbox_name()
        mailbox_id = self.instance.data.get('mailbox_id')
        qs = Q(Q(name=mailbox_name) | Q(id=mailbox_id))
        account.mailboxes.filter(qs).delete()
