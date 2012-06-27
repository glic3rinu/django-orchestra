from heapq import merge

class BillLinesBundle(object):
    invoice_lines = []
    invoice_lines_price = 0
    fee_lines = []
    fee_lines_price = 0
    invoice_recharge_lines = []
    invoice_recharge_lines_price = 0
    invoice_refound_lines = []
    invoice_refound_lines_price = 0
    fee_recharge_lines = []
    fee_recharge_lines_price = 0
    fee_refound_lines = []
    fee_refound_lines_price = 0
    
    def add(self, line, service):
        class_name = line.__class__.__name__ 
        if class_name == 'BillLine':
            if service.is_fee:
                self.fee_lines.append(line)
                self.fee_lines_price += line.price
            else:
                self.invoice_lines.append(line)
                self.invoice_lines_price += line.price
        elif class_name == 'AmendedBillLine':
            price = line.price
            if price > 0:
                if service.is_fee:
                    self.fee_recharge_lines.append(line)
                    self.fee_recharge_lines_price += price
                else:
                    self.invoice_recharge.append(line)
                    self.invoice_recharge_price += price
            else:
                if service.is_fee:
                    self.fee_refound_lines.append(line)
                    self.fee_refound_lines_price += price
                else:   
                    self.invoice_refound.append(line)
                    self.invoice_refound_price += price
        else: raise TypeError('I dont know what it is')
        
    def merge(self, bundle):
        self.invoice_lines = list(merge(self.invoice_lines, bundle.invoice_lines))
        self.fee_lines = list(merge(self.fee_lines, bundle.fee_lines))
        self.invoice_recharge_lines = list(merge(self.invoice_recharge_lines, bundle.invoice_recharge_lines))
        self.invoice_refound_lines = list(merge(self.invoice_refound_lines, bundle.invoice_refound_lines))
        self.fee_recharge_lines = list(merge(self.fee_recharge_lines, bundle.fee_recharge_lines))
        self.fee_refound_lines = list(merge(self.fee_refound_lines, bundle.fee_refound_lines))

        self.invoice_lines_price += bundle.invoice_lines_price
        self.fee_lines_price += bundle.fee_lines_price
        self.invoice_recharge_lines_price += bundle.invoice_recharge_lines_price
        self.invoice_refound_lines_price += bundle.invoice_refound_lines_price
        self.fee_recharge_lines_price += bundle.fee_recharge_lines_price
        self.fee_refound_lines_price += bundle.fee_refound_lines_price
        
        
    def save(self):
        for lines in [self.invoice_lines, self.fee_lines, self.invoice_recharge_lines, 
                      self.invoice_refound_lines, self.fee_recharge_lines, self.fee_refound_lines]:
            for line in lines:
                line.save()


def _create(bill_lines, contact, create_new_open=False): 
    open_invoice = None
    open_amendment_invoice = None
    open_amendment_invoice_2 = None
    
    if bill_lines.invoice_lines:
        if not create_new_open:
            open_invoice = Invoice.get_open(contact=contact)
        elif not open_invoice:
            open_invoice = Invoice.create(contact=contact)
        print 'yes'
        open_invoice.add(bill_lines.invoice_lines)
        
    if bill_lines.invoice_recharge_lines:
        if settings.CREATE_AMENDMENT_FOR_RECHARGE or settings.GROUP_REFOUND_AND_RECHARGE in settings.BILLING_INVOICES_AMENDMENT_BEHAVIOUR:
            if not create_new_open:
                open_amendment_invoice = AmendmentInvoice.get_open(contact=contact)
            elif not open_amendment_invoice: open_amendment_invoice = AmendmentInvoice.create(contact=contact)
            open_amendment_invoice.add(bill_lines.invoice_recharge_lines)
        else:
            if not open_invoice and not create_new_open:
                open_invoice = Invoice.get_open(contact=contact)
            if not open_invoice: open_invoice = Invoice.create(contact=contact)
            open_invoice.add(bill_lines.invoice_recharge_lines)
            
    if bill_lines.invoice_refound_lines:
        if settings.PUT_REFOUND_ON_OPEN_BILL_IF_POSITIVE in settings.BILLING_INVOICES_AMENDMENT_BEHAVIOUR: 
            if (open_invoice.total - bill_lines.invoice_refound_lines_price) > 0:
                if not open_invoice and not create_new_open:
                    open_invoice = Invoice.get_open(contact=contact)
                if not open_invoice: open_invoice = Invoice.create(contact=contact)
                open_invoice.add(bill_lines.invoice_refound_lines)
        elif settings.CREATE_AMENDMENT_FOR_REFOUND in settings.BILLING_INVOICES_AMENDMENT_BEHAVIOUR:
            open_amendment_invoice_2 = AmendmentInvoice.create(contact=contact)
            open_amendment_invoice_2.add(bill_lines.invoice_refound_lines)
        elif settings.PUT_REFOUND_ON_OPEN_BILL in settings.BILLING_INVOICES_AMENDMENT_BEHAVIOUR:
            open_invoice.add(bill_lines.invoice_refound_lines)
        elif settings.GROUP_REFOUND_AND_RECHARGE in settings.BILLING_INVOICES_AMENDMENT_BEHAVIOUR:
            if not open_amendment_invoice and not create_new_open:
                open_amendment_invoice = AmendmentInvoice.get_open(contact=contact)
            elif not open_amendment_invoice:
                open_amendment_invoice = AmendmentInvoice.create(contact=contact)
            open_amendment_invoice.add(bill_lines.invoice_refound_lines)                    
        else: raise TypeError('missconfigured invoice_amendment_behaviour')
    
    bills = []
    if open_invoice: 
        if commit: open_invoice.save()
        bills.append(open_invoice)
    if open_amendment_invoice: 
        if commit: open_amendment_invoice.save()
        bills.append(open_invoice)
    if open_amendment_invoice_2: 
        if commit: open_amendment_invoice_2.save()
        bills.append(open_invoice)

    if settings.BILLING_FEE_PER_FEE_LINE:
        for line in list(merge(merge(bill_lines.fee_lines, bill_lines.fee_refound_lines), bill_lines.fee_recharge_lines)):
            fee = Fee.create(lines=[line,], contact=contact)
            if commit: fee.save()
            bills.apend(fee)
    else: pass
        #TODO: make this shit
