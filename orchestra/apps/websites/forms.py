from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Website


class WebsiteAdminForm(forms.ModelForm):
    def clean(self):
        """ Prevent multiples domains on the same protocol """
        domains = self.cleaned_data.get('domains')
        if not domains:
            return self.cleaned_data
        protocol = self.cleaned_data.get('protocol')
        existing = []
        for domain in domains.all():
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
            if domain.websites.filter(qset).exclude(pk=self.instance.pk).exists():
                existing.append(domain.name)
        if existing:
            context = (', '.join(existing), protocol)
            raise ValidationError({
                'domains': 'A website is already defined for "%s" on protocol %s' % context
            })
        return self.cleaned_data

