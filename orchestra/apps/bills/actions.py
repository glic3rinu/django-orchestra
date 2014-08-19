def generate_bill(modeladmin, request, queryset):
    for bill in queryset:
        bill.close()
