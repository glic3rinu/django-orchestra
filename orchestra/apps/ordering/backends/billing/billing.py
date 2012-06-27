from billing.models import InvoiceLine, FeeLine, AmendedInvoiceLine, AmendedFeeLine, Bill
import decimal


def create_bill_line(order, price, ini, end, amendment_line=None):
    if amendment_line:
        if order.service.is_fee: line = AmendedFeeLine
        else: line = AmendedInvoiceLine
    else: 
        if order.service.is_fee: line = FeeLine
        else: line = InvoiceLine
    
    bill_line = line(order_id=order.pk, 
                     order_last_bill_date=order.last_bill_date,
                     order_billed_until=order.billed_until,
                     auto=True,
                     description=order.description, 
                     initial_date=ini,
                     final_date=end,
                     amount=order.get_metric(ini, end),
                     # unit_price=order.unit_price,
                     price=decimal.Decimal(str(price)),
                     tax=decimal.Decimal(str(order.tax.value)))
                    
    if amendment_line:
        bill_line.amendment = amendment_line
        
    return bill_line


def create_bills(bill_lines, contact):
    return Bill.create(contact, bill_lines)


def get_invoice_lines(order_id, initial_date, end_date):
    return InvoiceLine.objects.filter(order_id=order_id, 
                                      initial_date__lt=end_date, 
                                      final_date__gt=initial_date)
