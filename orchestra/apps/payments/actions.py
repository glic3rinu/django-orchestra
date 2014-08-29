def process_transactions(modeladmin, request, queryset):
    from .methods import SEPADirectDebit
    SEPADirectDebit().process(queryset)

