from common.widgets import ShowText
from datetime import datetime
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from models import Bill, BillLine, AmendedBillLine
import settings


def get_bill_change_link(bill, extra_name=''):
    if bill.__class__ is Bill:
        bill_cls = bill.subclass_instance.__class__
    else: bill_cls = bill.__class__        
    url = reverse('admin:billing_%s_change' % (bill_cls.__name__.lower()), args=(bill.id,))
    return '<a href="%(url)s">%(name)s</a>' % {'url': url, 'name': bill.ident + extra_name}


class BillLineForm(forms.ModelForm):
    line_number = forms.CharField(label=_("Line Number"), widget=ShowText(bold=True))
    order_id = forms.CharField(label=_("Order ID"),widget=ShowText())
    description = forms.CharField(label=_("Description"), widget=ShowText())
    initial_date = forms.CharField(label=_("Initial Date"), widget=ShowText())
    final_date = forms.CharField(label=_("Final Date"), widget=ShowText())
    price = forms.CharField(label=_("Price"), widget=ShowText())
    amount = forms.CharField(label=_("Metric"), widget=ShowText())
    tax = forms.CharField(label=_("Tax"), widget=ShowText())
    
    class Meta:
        model = BillLine
        fields = ('order_id', 'description', 'initial_date', 'final_date', 'price', 'amount', 'tax')

    def __init__(self, *args, **kwargs):
        super(BillLineForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.fields['line_number'].initial = instance.line_number


class AmendedBillLineForm(BillLineForm):
    amended_bill = forms.CharField(label=_("Amended Bill"), widget=ShowText(hidden=False), initial='', required=False)

    class Meta:
        model = AmendedBillLine

    def __init__(self, *args, **kwargs):
        super(AmendedBillLineForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            a_line = instance.subclass_instance.amended_line
            self.fields['amended_bill'].initial = "%s:%s" % (get_bill_change_link(a_line.bill), a_line.line_number)


def get_bill_form(cls):
    def now():
        # we need to pass a function to date field, otherwise the date gets fixed.
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    class BillForm(forms.ModelForm):
        ident = forms.CharField(widget=ShowText(bold=True))
        status = forms.CharField(widget=ShowText(), required=False, initial=_('Open'))
        date = forms.CharField(widget=ShowText(), required=False, initial=now)
        due_date = forms.CharField(widget=ShowText(), required=False, initial='')
        
        class Meta:
            model = cls
            exclude = ('status', 'date', 'due_date')
        
        
        def __init__(self, *args, **kwargs):
            print self.__class__.__bases__
            super(BillForm,self).__init__(*args, **kwargs)
            if 'instance' in kwargs:
                instance = kwargs['instance']
                self.fields['ident'].initial = instance.ident
                self.fields['status'].initial = instance.status_as_text
                self.fields['date'].initial = instance.date
                if instance.status != settings.OPEN:
                    self.fields['due_date'].initial = instance.due_date
            else:
                self.fields['ident'].initial=cls.get_new_open_ident()
                
    return BillForm
