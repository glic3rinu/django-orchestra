from django.core.urlresolvers import reverse
from django.shortcuts import redirect


def last(modeladmin, request, queryset):
    last_id = queryset.order_by('id').values_list('id', flat=True).first()
    url = reverse('admin:mailer_message_change', args=(last_id,))
    print(url)
    return redirect(url)
