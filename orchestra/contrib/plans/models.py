from functools import lru_cache

from django.core.validators import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_name
from orchestra.models import queryset
from orchestra.utils.python import import_class

from . import settings


class Plan(models.Model):
    name = models.CharField(_("name"), max_length=32, unique=True, validators=[validate_name])
    verbose_name = models.CharField(_("verbose_name"), max_length=128, blank=True)
    is_active = models.BooleanField(_("active"), default=True,
        help_text=_("Designates whether this account should be treated as active. "
                    "Unselect this instead of deleting accounts."))
    is_default = models.BooleanField(_("default"), default=False,
        help_text=_("Designates whether this plan is used by default or not."))
    is_combinable = models.BooleanField(_("combinable"), default=True,
        help_text=_("Designates whether this plan can be combined with other plans or not."))
    allow_multiple = models.BooleanField(_("allow multiple"), default=False,
        help_text=_("Designates whether this plan allow for multiple contractions."))
    
    def __str__(self):
        return self.get_verbose_name()
    
    def clean(self):
        self.verbose_name = self.verbose_name.strip()
    
    def get_verbose_name(self):
        return self.verbose_name or self.name


class ContractedPlan(models.Model):
    plan = models.ForeignKey(Plan, verbose_name=_("plan"), related_name='contracts')
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
        related_name='plans')
    
    class Meta:
        verbose_name_plural = _("plans")
    
    def __str__(self):
        return str(self.plan)
    
    @cached_property
    def active(self):
        return self.plan.is_active and self.account.is_active
    
    def clean(self):
        if not self.pk and not self.plan.allow_multiple:
            if ContractedPlan.objects.filter(plan=self.plan, account=self.account).exists():
                raise ValidationError("A contracted plan for this account already exists.")


class RateQuerySet(models.QuerySet):
    group_by = queryset.group_by
    
    def by_account(self, account):
        # Default allways selected
        return self.filter(
            Q(plan__is_default=True) |
            Q(plan__contracts__account=account)
        ).order_by('plan', 'quantity').select_related('plan', 'service')


class Rate(models.Model):
    service = models.ForeignKey('services.Service', verbose_name=_("service"),
        related_name='rates')
    plan = models.ForeignKey(Plan, verbose_name=_("plan"), related_name='rates', null=True,
        blank=True)
    quantity = models.PositiveIntegerField(_("quantity"), null=True, blank=True,
        help_text=_("See rate algorihm help text."))
    price = models.DecimalField(_("price"), max_digits=12, decimal_places=2)
    
    objects = RateQuerySet.as_manager()
    
    class Meta:
        unique_together = ('service', 'plan', 'quantity')
    
    def __str__(self):
        return "{}-{}".format(str(self.price), self.quantity)
    
    @classmethod
    @lru_cache()
    def get_methods(cls):
        return dict((method, import_class(method)) for method in settings.PLANS_RATE_METHODS)
    
    @classmethod
    @lru_cache()
    def get_choices(cls):
        choices = []
        for name, method in cls.get_methods().items():
            choices.append((name, method.verbose_name))
        return choices
    
    @classmethod
    def get_default(cls):
        return settings.PLANS_DEFAULT_RATE_METHOD
