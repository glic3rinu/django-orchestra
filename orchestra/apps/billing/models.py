from billing import settings
from common.utils.file import generate_pdf_stringio
from common.utils.models import group_by
from contacts.models import Contact
from datetime import datetime, timedelta
from django import template
from django.core.mail import EmailMessage
from django.db import models
from django.utils.translation import ugettext as _
from django.db.models import Q, F
import django.dispatch
from heapq import merge
from helpers import calculate_bases, calculate_taxes, calculate_total, calculate_total_bases_and_taxes


class BillLineManager(models.Manager):
    def get_all_related_pending_lines(self, line=None, **kwargs):
        #line = kwargs.pop('line')
        return self.filter(bill__status=settings.OPEN, 
            order_id=line.order_id, 
            order_last_bill_date=line.order_last_bill_date, 
            order_billed_until=line.order_billed_until ).filter(**kwargs)
        

class BaseBillLine(models.Model):
    description = models.CharField(max_length=256)
    initial_date = models.DateTimeField()
    final_date = models.DateTimeField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.IntegerField()
    tax = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        abstract = True   
    
    
class BudgetLine(BaseBillLine):
    budget = models.ForeignKey('billing.Budget', related_name='lines')
    
    @property
    def line_number(self):
        ix = 1
        for line in self.budget.lines.all().order_by('id'):
            if line == self: return ix
            ix += 1
    
    def __unicode__(self):
        return "%s:%s" % (self.budget.ident, self.line_number)
        
class BillLine(BaseBillLine):
    order_id = models.IntegerField() 
    order_last_bill_date = models.DateTimeField(null=True)
    order_billed_until = models.DateTimeField(null=True)
    auto = models.BooleanField(default=False)
    bill = models.ForeignKey('billing.Bill', related_name='lines')
    
    objects = BillLineManager()

    def __unicode__(self):
        return "%s:%s" % (self.bill.ident, self.line_number)
  
    @property
    def discounts(self):
        return self.discounts_set.all()

    def save(self, *args, **kwargs):
        if not self.bill_id: 
            self.bill_id = self.bill.id
        super(BillLine, self).save(*args, **kwargs)

    @property
    def subclass_instance(self):
        try: invoice = self.invoiceline
        except self.DoesNotExist:
            try: fee = self.feeline
            except self.DoesNotExist: 
                try: a_invoice = self.amendedinvoiceline
                except self.DoesNotExist:
                    try: a_fee = self.amendedfeeline
                    except self.DoesNotExist: raise AttributeError("Dont know what subclass is")
                    else: return a_fee
                else: return a_invoice
            else: return fee
        else: return invoice

    def auto_create_amend(self):
        sub_cls = self.subclass_instance.__class__
        if sub_cls is InvoiceLine:
            a_cls = AmendedInvoiceLine
        elif sub_cls is FeeLine:
            a_cls = AmendedFeeLine
        else: 
            #Asum that it must be an amended line
            a_cls = sub_cls
            
        a_line = a_cls(
            order_id=self.order_id,
#            order_last_bill_date=self.order_last_bill_date,
#            order_billed_until=self.order_billed_until,
            description=self.description,
            initial_date=self.initial_date,
            final_date=self.final_date,
            price=-(self.price),
            amount=self.amount,
            tax=self.tax,
            amended_line=self)
        return a_line

    @property
    def line_number(self):
        ix = 1
        for line in self.bill.lines.all().order_by('id'):
            if line == self: return ix
            ix += 1


class FeeLine(BillLine):
    pass


class InvoiceLine(BillLine):
    pass


class AmendedBillLine(BillLine):
    amended_line = models.ForeignKey(BillLine, related_name='%(class)s_lines')
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return str(self.description) + ' '+ str(self.amended_line)
        
    @classmethod
    def create(cls, order, price, initial_date, final_date, line):
        n_line = super(AmendedBillLine, self).create(*args, **kwargs)
        n_line.amended_line = line
        return n_line


class AmendedInvoiceLine(AmendedBillLine):
    pass


class AmendedFeeLine(AmendedBillLine):
    pass


class Discount(models.Model):
    MANUAL='M'
    INCOMPLETE='I'
    PACK='P'
    RANGE='R'

    CATEGORY_CHOICES=(
        (MANUAL, _('Manual')),
        (INCOMPLETE, _('Incomplete')),
        (PACK, _('Pack')),
        (RANGE, _('Range')),)
        
    bill_line = models.ForeignKey(BillLine)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default=MANUAL)


bill_pre_send = django.dispatch.Signal(providing_args=["bill"])


class BaseBill(models.Model):
    ident = models.CharField(max_length=16, unique=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    contact = models.ForeignKey('contacts.Contact', related_name='%(class)s_contact')
    #base = models.DecimalField(max_digits=12, decimal_places=2)
    #tax = models.DecimalField(max_digits=12, decimal_places=2)
    comments = models.TextField(blank=True)
    html = models.TextField(blank=True) 
    status = models.CharField(max_length=16, choices=settings.BILLING_STATUS_CHOICES, default=settings.OPEN, blank=True)    

    class Meta:
        abstract = True
        ordering = ['-modified']
    
    def __unicode__(self):
        return str(self.ident)    

    @property
    def type(self):
        return self.subclass_instance.__class__.__name__

    @property
    def status_is_open(self):
        return True if self.status == settings.OPEN else False

    @property
    def status_as_text(self):
        for choice in settings.BILLING_STATUS_CHOICES:
            if choice[0] == self.status:
                return choice[1]

    @property
    def bases(self):
        """ 
            Calculates bases on the fly, due problems rounding bills with multiple taxes.
            Another solution could be create a MTO relationship with a new "Bases" model.
        """
        return calculate_bases(self.lines.all())
        
    @property
    def taxes(self): 
        return calculate_taxes(self.lines.all(), self.bases)
                
    @property
    def total(self):
        return calculate_total(self.bases, self.taxes)

    def add(self, lines):
        for line in lines:
            line.bill = self

    @classmethod
    def get_new_ident(cls):
        #Bill number is reset every Natural Year. 
        year = datetime.now().strftime("%Y")
        num = cls.objects.filter(Q(date__year=year) & ~Q(status=settings.OPEN)).count() + 1
        number = (int(eval('settings.BILLING_%s_ID_LENGTH' % cls.__name__.upper())) - len(str(num))) * "0" + str(num)
        
        return '%(prefix)s%(year)s%(number)s' % {'prefix': eval('settings.BILLING_%s_ID_PREFIX' % cls.__name__.upper()),
            'year': year, 'number': number}   
              
    @classmethod
    def get_new_open_ident(cls):
        year = datetime.now().strftime("%Y")
        size = int(eval('settings.BILLING_%s_ID_LENGTH' % cls.__name__.upper()))
        try: num = int(cls.objects.filter(status=settings.OPEN, date__year=year).order_by('-ident')[0].ident[-size:])
        except IndexError: num = 0
        number = (int(size - len(str(num))) * "0" + str(num+1))
        
        return 'OPEN%(prefix)s%(year)s%(number)s' % {'prefix': eval('settings.BILLING_%s_ID_PREFIX' % cls.__name__.upper()),
            'year': year, 'number': number} 

    @classmethod
    def get_open(cls, contact):
        #TODO: this default ordering is desirable?
        try: return cls.objects.filter(contact=contact, status=settings.OPEN).order_by('-date')[0]
        except IndexError: return None
    
    @classmethod
    def _create(cls, lines, contact, create_new_open):
        open_bill = cls.get_open(contact=contact)
        now = datetime.now()
        if create_new_open or not open_bill:
            ident = cls.get_new_open_ident()                
            open_bill = cls(contact = contact,
                             date = now,
                             due_date = now + timedelta(days=settings.BILLING_DUE_DATE_DAYS),
                             ident = ident,
                             status = settings.OPEN)
        
        open_bill.save()
        for line in lines:
            line.bill = open_bill
            line.save()
        return open_bill
        
    @classmethod
    def create(cls, contact, bill_lines, create_new_open=False):

        bills = []
        g_lines = group_by(list, '__class__', bill_lines, dictionary=True, queryset=False)
        #TODO: all orders in amendment must have the same tax            
        for group in g_lines:
            if group == FeeLine: 
                for line in g_lines[group]:
                    bills.append(Fee._create([line], contact, create_new_open=True))
            else: 
                if group == InvoiceLine: bill = Invoice
                elif group == AmendedInvoiceLine: bill = AmendmentInvoice
                elif group == AmendedFeeLine: bill = AmendmentFee  
                bills.append(bill._create(g_lines[group], contact, create_new_open=create_new_open))
        return bills
                
    
    def close(self):
        #TODO: do not close invoices with 0 lines
        now = datetime.now()
        self.date = now
        self.due_date = now + timedelta(days=settings.BILLING_DUE_DATE_DAYS)
        self.ident = self.__class__.get_new_ident()
        self.status = settings.CLOSED
        self.html = self._generate_html()
        self.save()
        
    def send(self):

        bill_pre_send.send(sender=Bill, bill=self)
        
        email_to = [self.contact.billing_contact.email,]
        email_from = Contact.get_isp().billing_contact.email
        email_bcc = []
        email_subject = '%s %s' % (self.type, self.ident)
        email_body = 'here is the bill.'
        
        message = EmailMessage(email_subject, email_body, email_from, email_to, email_bcc)
        message.attach('%s.pdf' % (self.ident), self.get_pdf().getvalue() , 'application/pdf')
        message.send()


        self.status = settings.SEND
        self.save()
    
    def mark_as_returned(self):
        self.status = settings.RETURNED
        self.save()

    def mark_as_payd(self):
        self.status = settings.PAYD
        self.save()

    def mark_as_irrecovrable(self):
        self.status = settings.IRRECOVRABLE
        self.save()

    def get_pdf(self):
        html = self.html if self.html else self._generate_html()
        return generate_pdf_stringio(html)
        
    def _generate_html(self):
        lines = self.lines.all()
        total, bases, taxes = calculate_total_bases_and_taxes(lines)
        
        sender_bill_data = self.contact.__class__.get_isp().billing_data
        contact_bill_data = self.contact.billing_data

        #TODO: context = locals()
        context_dict = { 'bill_type': self._meta.verbose_name.capitalize(),
                         'sender_bill_data': sender_bill_data, 
                         'contact_bill_data': contact_bill_data,
                         'bill': self,
                         'bases': bases,
                         'taxes': taxes,
                         'total': total, 
                         'lines': lines }

        context = template.Context(context_dict)
        html = template.loader.get_template(eval('settings.BILLING_%s_TEMPLATE' % self.type.upper())).render(context)
        html = html.replace('-pageskip-', '<pdf:nextpage />')
        
        return html 
    
    @property
    def seller(self):
        return self.contact.__class__.get_isp()
    
    @property
    def buyer(self):
        return self.contact
    
class Bill(BaseBill):
    @property
    def subclass_instance(self):
        try: invoice = self.invoice
        except Invoice.DoesNotExist:
            try: fee = self.fee
            except Fee.DoesNotExist: 
                try: a_invoice = self.amendmentinvoice
                except AmendmentInvoice.DoesNotExist:
                    try: a_fee = self.amendmentfee
                    except AmendmentFee.DoesNotExist:
                        budget = self.budget
                        return budget
                    else: return a_fee
                else: return a_invoice
            else: return fee
        else: return invoice
                    
    @classmethod
    def get_subclasses(cls):
        return [Invoice, Fee, AmendmentInvoice, AmendmentFee]
  
class Invoice(Bill):
    """ 
        Invoices through the time of the entitys. It store an HTML version of the
        invoice in order to allow modifications
    """

class AmendmentInvoice(Bill):
    """ 
        Amendment invoices. All orders listed in orders will be refounded and 
        cancelled 
    """
    
class Fee(Bill):
    pass
    
    
class AmendmentFee(Bill):
    """ 
        Amendment Quotas. All orders listed in orders will be refounded and 
        cancelled 
    """
 
class Budget(BaseBill):
    """ Manual Budgets """
    
    
