from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _


class HasMailboxListFilter(SimpleListFilter):
    """ Filter addresses whether they have any mailbox or not """
    title = _("has mailbox")
    parameter_name = 'has_mailbox'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("True")),
            ('False', _("False")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(mailboxes__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(mailboxes__isnull=True)
        return queryset


class HasForwardListFilter(HasMailboxListFilter):
    """ Filter addresses whether they have any mailbox or not """
    title = _("has forward")
    parameter_name = 'has_forward'
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.exclude(forward='')
        elif self.value() == 'False':
            return queryset.filter(forward='')
        return queryset


class HasAddressListFilter(HasMailboxListFilter):
    """ Filter addresses whether they have any mailbox or not """
    title = _("has address")
    parameter_name = 'has_address'
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(addresses__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(addresses__isnull=True)
        return queryset
