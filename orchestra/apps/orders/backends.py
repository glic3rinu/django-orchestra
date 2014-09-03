import datetime

from orchestra.apps.bills.models import Invoice, Fee, BillLine, BillSubline


class BillsBackend(object):
    def create_bills(self, account, lines):
        invoice = None
        bills = []
        for order, nominal_price, size, ini, end, discounts in lines:
            service = order.service
            if service.is_fee:
                fee, __ = Fee.objects.get_or_create(account=account, status=Fee.OPEN)
                line = fee.lines.create(
                        rate=service.nominal_price,
                        amount=size,
                        total=nominal_price, tax=0,
                        description="{ini} to {end}".format(
                            ini=ini.strftime("%b, %Y"),
                            end=(end-datetime.timedelta(seconds=1)).strftime("%b, %Y")),
                )
                self.create_sublines(line, discounts)
                bills.append(fee)
            else:
                if invoice is None:
                    invoice, __ = Invoice.objects.get_or_create(account=account,
                            status=Invoice.OPEN)
                    bills.append(invoice)
                description = order.description 
                if service.billing_period != service.NEVER:
                    description += " {ini} to {end}".format(
                        ini=ini.strftime("%b, %Y"),
                        end=(end-datetime.timedelta(seconds=1)).strftime("%b, %Y"))
                line = invoice.lines.create(
                    description=description,
                    rate=service.nominal_price,
                    amount=size,
                    total=nominal_price,
                    tax=service.tax,
                )
                self.create_sublines(line, discounts)
        return bills
    
    def create_sublines(self, line, discounts):
        for name, value in discounts:
            line.sublines.create(
                description=_("Discount per %s") % name,
                total=value,
            )
