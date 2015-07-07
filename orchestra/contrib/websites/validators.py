from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from .models import Website


def validate_domain_protocol(website, domain, protocol):
    if protocol == Website.HTTP:
        qset = Q(
            Q(protocol=Website.HTTP) |
            Q(protocol=Website.HTTP_AND_HTTPS) |
            Q(protocol=Website.HTTPS_ONLY)
        )
    elif protocol == Website.HTTPS:
        qset = Q(
            Q(protocol=Website.HTTPS) |
            Q(protocol=Website.HTTP_AND_HTTPS) |
            Q(protocol=Website.HTTPS_ONLY)
        )
    elif protocol in (Website.HTTP_AND_HTTPS, Website.HTTPS_ONLY):
        qset = Q()
    else:
        raise ValidationError({
            'protocol': _("Unknown protocol %s") % protocol
        })
    if domain.websites.filter(qset).exclude(pk=website.pk).exists():
        raise ValidationError({
            'domains': 'A website is already defined for "%s" on protocol %s' % (domain, protocol),
        })


def validate_server_name(domains):
    if domains:
        for domain in domains:
            if not domain.name.startswith('*'):
                return
    raise ValidationError(_("At least one non-wildcard domain should be provided."))
