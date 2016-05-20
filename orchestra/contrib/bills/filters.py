from django.contrib.admin import SimpleListFilter
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from . models import Bill


class BillTypeListFilter(SimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = 'Type'
    parameter_name = ''
    
    def __init__(self, request, *args, **kwargs):
        super(BillTypeListFilter, self).__init__(request, *args, **kwargs)
        self.request = request
    
    def lookups(self, request, model_admin):
        return (
            ('bill', _("All")),
            ('invoice', _("Invoice")),
            ('fee', _("Fee")),
            ('proforma', _("Pro-forma")),
            ('amendmentfee', _("Amendment fee")),
            ('amendmentinvoice', _("Amendment invoice")),
        )
    
    def queryset(self, request, queryset):
        return queryset
    
    def value(self):
        return self.request.path.split('/')[-2]
    
    def choices(self, cl):
        query = self.request.GET.urlencode()
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': reverse('admin:bills_%s_changelist' % lookup) + '?%s' % query,
                'display': title,
            }


class TotalListFilter(SimpleListFilter):
    title = _("total")
    parameter_name = 'total'
    
    def lookups(self, request, model_admin):
        return (
            ('gt', mark_safe("total &gt; 0")),
            ('lt', mark_safe("total &lt; 0")),
            ('eq', "total = 0"),
            ('ne', mark_safe("total &ne; 0")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'gt':
            return queryset.filter(approx_total__gt=0)
        elif self.value() == 'eq':
            return queryset.filter(approx_total=0)
        elif self.value() == 'lt':
            return queryset.filter(approx_total__lt=0)
        elif self.value() == 'ne':
            return queryset.exclude(approx_total=0)
        return queryset


class HasBillContactListFilter(SimpleListFilter):
    """ Filter Nodes by group according to request.user """
    title = _("has bill contact")
    parameter_name = 'bill'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("Yes")),
            ('False', _("No")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(billcontact__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(billcontact__isnull=True)


class PaymentStateListFilter(SimpleListFilter):
    title = _("payment state")
    parameter_name = 'payment_state'
    
    def lookups(self, request, model_admin):
        return (
            ('OPEN', _("Open")),
            ('PAID', _("Paid")),
            ('PENDING', _("Pending")),
            ('BAD_DEBT', _("Bad debt")),
        )
    
    def queryset(self, request, queryset):
        # FIXME use queryset.computed_total instead of approx_total, bills.admin.BillAdmin.get_queryset
        Transaction = queryset.model.transactions.field.remote_field.related_model
        if self.value() == 'OPEN':
            return queryset.filter(Q(is_open=True)|Q(type=queryset.model.PROFORMA))
        elif self.value() == 'PAID':
            zeros = queryset.filter(approx_total=0, approx_total__isnull=True)
            zeros = zeros.values_list('id', flat=True)
            amounts = Transaction.objects.exclude(bill_id__in=zeros).secured().group_by('bill_id')
            paid = []
            relevant = queryset.exclude(approx_total=0, approx_total__isnull=True, is_open=True)
            for bill_id, total in relevant.values_list('id', 'approx_total'):
                try:
                    amount = sum([t.amount for t in amounts[bill_id]])
                except KeyError:
                    pass
                else:
                    if abs(total) <= abs(amount):
                        paid.append(bill_id)
            return queryset.filter(
                Q(approx_total=0) |
                Q(approx_total__isnull=True) |
                Q(id__in=paid)
            ).exclude(is_open=True)
        elif self.value() == 'PENDING':
            has_transaction = queryset.exclude(transactions__isnull=True)
            non_rejected = has_transaction.exclude(transactions__state=Transaction.REJECTED)
            paid = non_rejected.exclude(transactions__state=Transaction.SECURED)
            paid = paid.values_list('id', flat=True).distinct()
            return queryset.filter(pk__in=paid)
        elif self.value() == 'BAD_DEBT':
            closed = queryset.filter(is_open=False).exclude(approx_total=0)
            return closed.filter(
                Q(transactions__state=Transaction.REJECTED) |
                Q(transactions__isnull=True)
            )


class AmendedListFilter(SimpleListFilter):
    title = _("amended")
    parameter_name = 'amended'
    
    def lookups(self, request, model_admin):
        return (
            ('3', _("Closed amends")),
            ('2', _("Open amends")),
            ('1', _("Any amends")),
            ('0', _("No amends")),
        )
    
    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        amended = queryset.filter(amends__isnull=False)
        if self.value() == '1':
            return amended.distinct()
        elif self.value() == '2':
            return amended.filter(amends__is_open=True).distinct()
        elif self.value() == '3':
            return amended.filter(amends__is_open=False).distinct()
        elif self.value() == '0':
            return queryset.filter(amends__isnull=True).distinct()
