import ast
from billing.models import Bill, Invoice, Fee, AmendmentFee, AmendmentInvoice
from common.utils.admin import insert_inline
from common.utils.models import group_by
from common.utils.response import download_files
from common.widgets import ShowText
from contacts.models import Contact
from django import forms
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.utils.html import escape
from django.utils.translation import ugettext as _
from payments import settings
from models import PaymentDetails, Transaction
from plugins import PaymentMethod


class PaymentDetailsForm(forms.ModelForm):
    data = forms.CharField(label='Data', widget=forms.widgets.TextInput(attrs={'size':'100'}))
    
    def clean_data(self):
        error_msg = "Data must be formated as python dict: {'key1': 'val1', 'key2': 'val2'}"
        data = self.cleaned_data['data']
        # Check if data is a dict
        try: data_dict = ast.literal_eval(data)
        except: raise forms.ValidationError(error_msg)
        else:
            if type(data_dict) != type({}):
                raise forms.ValidationError(error_msg)
        # Call custom clean_data validation
        method = self.cleaned_data['method']
        method.get_plugin().clean_data(self, data_dict)
        return data


class PaymentDetailsInline(admin.TabularInline):
    model = PaymentDetails
    extra = 1
    form = PaymentDetailsForm
    
insert_inline(Contact, PaymentDetailsInline)


class TransactionInlineForm(forms.ModelForm):
    transaction_id = forms.CharField(label=_("Transaction ID"), widget=ShowText(bold=True))
    status = forms.CharField(label=_("Status"),widget=ShowText())
    method = forms.CharField(label=_("Method"), widget=ShowText())
    total = forms.CharField(label=_("Total"), widget=ShowText())
    currency = forms.CharField(label=_("Currency"), widget=ShowText(), required=False)
    created = forms.CharField(label=_("Created"), widget=ShowText())
    modified = forms.CharField(label=_("Modified"), widget=ShowText())
    
    class Meta:
        model = Transaction
        fields = ()
    
    def __init__(self, *args, **kwargs):
        super(TransactionInlineForm, self).__init__(*args, **kwargs)
        #FIXME: why I need to query for instance.id, self.instance is not enought?
        if self.instance.id:
        #TODO: make this form completly read_only, otherwise it breaks the admin when save() if we don't make this model/form decoulping:
            for field in ('status', 'method', 'currency', 'created', 'modified'):
                self.fields[field].initial = getattr(self.instance, field)
            self.fields['transaction_id'].initial = self.instance.pk


class TransactionInline(admin.TabularInline):
    model = Transaction
    max_num = 0
    extra = 0
    form = TransactionInlineForm
    can_delete = False

insert_inline(Bill, TransactionInline)


TRANSACTION_STATE_COLORS = {settings.WAITTING_PROCESSING: "darkorange",
                            settings.WAITTING_CONFIRMATION: "blue",
                            settings.CONFIRMED: "green",
                            settings.REJECTED: "red",
                            settings.LOCKED: "magenta",
                            settings.DISCARTED: "gray",}


def colored_status(transaction):
    #TODO: use verbose human readable of status
    state = escape(transaction.status)
    color = TRANSACTION_STATE_COLORS.get(transaction.status, "black")
    return """<b><span style="color: %s;">%s</span></b>""" % (color, state)
colored_status.short_description = _("status")
colored_status.allow_tags = True
colored_status.admin_order_field = 'status'


def contact_link(self):
    url = reverse('admin:contacts_contact_change', args=[self.contact.pk])
    return '<a href="%s">%s</a>' % (url, self.contact)
contact_link.short_description = _("Contact")
contact_link.allow_tags = True
contact_link.admin_order_field = 'contact'


def bill_link(self):
    url = reverse('admin:billing_bill_change', args=[self.bill.pk])
    return '<a href="%s">%s</a>' % (url, self.bill)
bill_link.short_description = _("Bill")
bill_link.allow_tags = True
bill_link.admin_order_field = 'bill'


def total_bold(self):
    return "<b>%s</b>" % self.total
total_bold.short_description = _("Total")
total_bold.allow_tags = True
total_bold.admin_order_field = 'total'


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'method', colored_status, total_bold, bill_link, contact_link, 'created', 'modified',)
    list_filter = ('status', 'method')
    date_hierarchy = 'created'
    search_fields = ['bill__ident', 'bill__contact__name', 'id', 'method__name', 'status']
    actions = ['process_transactions', 'confirm', 'reject']

    def process_transactions(modeladmin, request, queryset):
        query_dict = group_by(Transaction, 'method', queryset, dictionary=True)
        files = []
        for key in query_dict.keys():
            gateway = key.get_plugin()
            file = gateway.process(query_dict[key])
            if file: 
                files.append({'filename': '%s_transaction_%s.%s' % (gateway.name, len(files), gateway.extention), 
                              'file': file })
                              
            for transaction in query_dict[key]:
                if transaction.status == settings.WAITTING_PROCESSING:
                    transaction.status = settings.WAITTING_CONFIRMATION
                # Update modified time 
                transaction.save()
                    
        messages.add_message(request, messages.INFO, _("All Selected transactions has been processed"))
        return download_files(files, mimetype=gateway.mimetype)
        
    process_transactions.short_description = _('Process transactions')

    @transaction.commit_on_success
    def confirm(modeladmin, request, queryset):
        for transaction in queryset:
            transaction.confirm()
        messages.add_message(request, messages.INFO, _("All Selected transactions has been confirmed"))
    confirm.short_description = _('Confirm')
    
    @transaction.commit_on_success
    def reject(modeladmin, request, queryset):
        for transaction in queryset:
            transaction.reject()
        messages.add_message(request, messages.INFO, _("All Selected transactions has been rejected"))
    reject.short_description = _('Reject')


admin.site.register(Transaction, TransactionAdmin)
