from django import forms
from django.core.exceptions import ValidationError


class WebsiteAdminForm(forms.ModelForm):
    def clean(self):
        """ Prevent multiples domains on the same port """
        domains = self.cleaned_data.get('domains')
        port = self.cleaned_data.get('port')
        existing = []
        for domain in domains.all():
            if domain.websites.filter(port=port).exclude(pk=self.instance.pk).exists():
                existing.append(domain.name)
        if existing:
            context = (', '.join(existing), port)
            raise ValidationError({
                'domains': 'A website is already defined for "%s" on port %s' % context
            })
        return self.cleaned_data

