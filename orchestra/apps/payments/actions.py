from .methods import BankTransfer

def process_transactions(modeladmin, request, queryset):
    BankTransfer().process(queryset)

