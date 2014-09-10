import datetime

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.bills.models import Invoice, Fee, BillLine, BillSubline


class BillsBackend(object):
    def create_bills(self, account, lines):
        invoice = None
        bills = []
        for line in lines:
            service = line.order.service
            if service.is_fee:
                fee, __ = Fee.objects.get_or_create(account=account, status=Fee.OPEN)
                storedline = fee.lines.create(
                        rate=service.nominal_price,
                        amount=line.size,
                        total=line.subtotal, tax=0,
                        description=self.format_period(line.ini, line.end),
                )
                self.create_sublines(storedline, line.discounts)
                bills.append(fee)
            else:
                if invoice is None:
                    invoice, __ = Invoice.objects.get_or_create(account=account,
                            status=Invoice.OPEN)
                    bills.append(invoice)
                description = line.order.description 
                if service.billing_period != service.NEVER:
                    description += " %s" % self.format_period(line.ini, line.end)
                storedline = invoice.lines.create(
                    description=description,
                    rate=service.nominal_price,
                    amount=line.size,
                    # TODO rename line.total > subtotal
                    total=line.subtotal,
                    tax=service.tax,
                )
                self.create_sublines(storedline, line.discounts)
        return bills
    
    def format_period(self, ini, end):
        ini = ini.strftime("%b, %Y")
        end = (end-datetime.timedelta(seconds=1)).strftime("%b, %Y")
        if ini == end:
            return ini
        return _("{ini} to {end}").format(ini=ini, end=end)
    
    
    def create_sublines(self, line, discounts):
        for discount in discounts:
            line.sublines.create(
                description=_("Discount per %s") % discount.type,
                total=discount.total,
            )
