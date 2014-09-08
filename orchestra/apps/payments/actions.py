from .methods import PaymentMethod
def process_transactions(modeladmin, request, queryset):
    for method, transactions in queryset.group_by('source__method'):
        if method is not None:
            PaymentMethod.get_plugin(method)().process(transactions)
