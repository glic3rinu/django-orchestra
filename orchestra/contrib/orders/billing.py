from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.bills.models import Invoice, Fee, ProForma


class BillsBackend(object):
    def create_bills(self, account, lines, **options):
        bill = None
        ant_bill = None
        bills = []
        create_new = options.get('new_open', False)
        proforma = options.get('proforma', False)
        for line in lines:
            quantity = line.metric*line.size
            if quantity == 0:
                continue
            service = line.order.service
            # Create bill if needed
            if proforma:
                if ant_bill is None:
                    if create_new:
                        bill = ProForma.objects.create(account=account)
                    else:
                        bill = ProForma.objects.filter(account=account, is_open=True).last()
                        if bill:
                            bill.updated()
                        else:
                            bill = ProForma.objects.create(account=account, is_open=True)
                    bills.append(bill)
                else:
                    bill = ant_bill
                ant_bill = bill
            elif service.is_fee:
                bill = Fee.objects.create(account=account)
                bills.append(bill)
            else:
                if ant_bill is None:
                    if create_new:
                        bill = Invoice.objects.create(account=account)
                    else:
                        bill = Invoice.objects.filter(account=account, is_open=True).last()
                        if bill:
                            bill.updated()
                        else:
                            bill = Invoice.objects.create(account=account, is_open=True)
                    bills.append(bill)
                else:
                    bill = ant_bill
                ant_bill = bill
            # Create bill line
            billine = bill.lines.create(
                rate=service.nominal_price,
                quantity=line.metric*line.size,
                verbose_quantity=self.get_verbose_quantity(line),
                subtotal=line.subtotal,
                tax=service.tax,
                description=self.get_line_description(line),
                start_on=line.ini,
                end_on=line.end if service.billing_period != service.NEVER else None,
                order=line.order,
                order_billed_on=line.order.old_billed_on,
                order_billed_until=line.order.old_billed_until
            )
            self.create_sublines(billine, line.discounts)
        return bills
    
#    def format_period(self, ini, end):
#        ini = ini.strftime("%b, %Y")
#        end = (end-datetime.timedelta(seconds=1)).strftime("%b, %Y")
#        if ini == end:
#            return ini
#        return _("{ini} to {end}").format(ini=ini, end=end)
    
    def get_line_description(self, line):
        service = line.order.service
        description = line.order.description
        return description
    
    def get_verbose_quantity(self, line):
        metric = format(line.metric, '.2f').rstrip('0').rstrip('.')
        metric = metric.strip('0').strip('.')
        size = format(line.size, '.2f').rstrip('0').rstrip('.')
        size = size.strip('0').strip('.')
        if metric == '1':
            return size
        if size == '1':
            return metric
        return "%s&times;%s" % (metric, size)
    
    def create_sublines(self, line, discounts):
        for discount in discounts:
            line.sublines.create(
                description=_("Discount per %s") % discount.type.lower(),
                total=discount.total,
                type=discount.type,
            )
