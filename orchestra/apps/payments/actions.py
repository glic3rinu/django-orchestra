def process_transactions(modeladmin, request, queryset):
    for source, transactions in queryset.group_by('source'):
        if source:
            source.method_class().process(transactions)
