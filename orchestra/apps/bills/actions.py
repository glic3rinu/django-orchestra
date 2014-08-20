from django.http import HttpResponse


def generate_bill(modeladmin, request, queryset):
    bill = queryset.get()
    bill.close()
    return HttpResponse(bill.html)
