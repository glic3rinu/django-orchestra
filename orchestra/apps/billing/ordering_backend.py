from ordering.models import Order

def get_order(pk):
    return Order.objects.get(pk=pk)
