from django.core.urlresolvers import reverse
from django.shortcuts import redirect


def last(modeladmin, request, queryset):
    last = queryset.model.objects.latest('id')
    url = reverse('admin:mailer_message_change', args=(last.pk,))
    return redirect(url)
