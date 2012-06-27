from common.utils.file import generate_pdf_stringio
import cStringIO as StringIO
from datetime import datetime
from django import template, forms
from payments.plugins import PaymentMethod
import settings


class BankTransfer(PaymentMethod):
    name = 'bank_transfer'
    title = 'Bank Transfer'
    mimetype = 'application/x-pdf'
    extention = 'pdf'

    def process(self, transactions):
        report = self._generate_bank_transfer_report(transactions)
        return report

    def get_transaction_data(self, buyer_data, seller_data, bill, id):
        data = {'account': buyer_data.account,
                'concept': bill.ident,}
        return data
        
    def _generate_bank_transfer_report(self, transactions):
        charge = transactions.filter(total__gt=0)
        refound = transactions.filter(total__lt=0)
        zero = transactions.filter(total=0)
        date = datetime.now()
        context = template.Context({'charge_transactions': charge,
                                    'refound_transactions': refound,
                                    'zero_transactions': zero,
                                    'date': date})
                                    
        html = template.loader.get_template(settings.REPORT_TEMPLATE).render(context)
        html = html.replace('-pageskip-', '<pdf:nextpage />')
        return generate_pdf_stringio(html)
        
    def clean_data(self, form, data_dict):
        #TODO: clean account with control digits 
        data = form.cleaned_data['data']
        if 'account' not in data_dict.keys():
            raise forms.ValidationError("Please provide 'account' data.")


