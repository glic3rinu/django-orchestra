import datetime

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.bills.models import Invoice, Fee, ProForma, BillLine, BillSubline


class BillsBackend(object):
    def create_bills(self, account, lines, **options):
        bill = None
        bills = []
        create_new = options.get('new_open', False)
        proforma = options.get('proforma', False)
        for line in lines:
            service = line.order.service
            # Create bill if needed
            if bill is None or service.is_fee:
                if proforma:
                    if create_new:
                        bill = ProForma.objects.create(account=account)
                    else:
                        bill = ProForma.objects.filter(account=account, is_open=True).last()
                        if not bill:
                            bill = ProForma.objects.create(account=account, is_open=True)
                elif service.is_fee:
                    bill = Fee.objects.create(account=account)
                else:
                    if create_new:
                        bill = Invoice.objects.create(account=account)
                    else:
                        bill = Invoice.objects.filter(account=account, is_open=True).last()
                        if not bill:
                            bill = Invoice.objects.create(account=account, is_open=True)
                bills.append(bill)
            # Create bill line
            billine = bill.lines.create(
                    rate=service.nominal_price,
                    quantity=line.metric*line.size,
                    subtotal=line.subtotal,
                    tax=service.tax,
                    description=self.get_line_description(line),
            )
            self.create_sublines(billine, line.discounts)
        return bills
    
    def format_period(self, ini, end):
        ini = ini.strftime("%b, %Y")
        end = (end-datetime.timedelta(seconds=1)).strftime("%b, %Y")
        if ini == end:
            return ini
        return _("{ini} to {end}").format(ini=ini, end=end)
    
    def get_line_description(self, line):
        service = line.order.service
        if service.is_fee:
            return self.format_period(line.ini, line.end)
        description = line.order.description
        if service.billing_period != service.NEVER:
            description += " %s" % self.format_period(line.ini, line.end)
        if service.metric and service.billing_period != service.NEVER and service.pricing_period == service.NEVER:
            metric = format(line.metric, '.2f').rstrip('0').rstrip('.')
            size = format(line.size, '.2f').rstrip('0').rstrip('.')
            description += " (%s*%s)" % (metric, size)
        return description
    
    def create_sublines(self, line, discounts):
        for discount in discounts:
            line.sublines.create(
                description=_("Discount per %s") % discount.type,
                total=discount.total,
            )
