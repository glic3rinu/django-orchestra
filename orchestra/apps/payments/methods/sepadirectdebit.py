import os
import lxml.builder
from lxml import etree
from lxml.builder import E
from StringIO import StringIO

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_iban.forms import IBANFormField
from django_iban.validators import IBANValidator, IBAN_COUNTRY_CODE_LENGTH
from rest_framework import serializers

from .. import settings
from .options import PaymentSourceDataForm, PaymentMethod


class SEPADirectDebitForm(PaymentSourceDataForm):
    iban = IBANFormField(label='IBAN',
            widget=forms.TextInput(attrs={'size': '50'}))
    name = forms.CharField(max_length=128, label=_("Name"),
            widget=forms.TextInput(attrs={'size': '50'}))


class SEPADirectDebitSerializer(serializers.Serializer):
    iban = serializers.CharField(label='IBAN', validators=[IBANValidator()],
            min_length=min(IBAN_COUNTRY_CODE_LENGTH.values()), max_length=34)
    name = serializers.CharField(label=_("Name"), max_length=128)


class SEPADirectDebit(PaymentMethod):
    verbose_name = _("Direct Debit")
    label_field = 'name'
    number_field = 'iban'
    process_credit = True
    form = SEPADirectDebitForm
    serializer = SEPADirectDebitSerializer
    
    def process(self, transactions):
        debts = []
        credits = []
        for transaction in transactions:
            if transaction.amount < 0:
                credits.append(transaction)
            else:
                debts.append(transaction)
        if debts:
            self._process_debts(debts)
        if credits:
            self._process_credits(credits)
    
    def _process_credits(self, transactions):
        from ..models import PaymentProcess
        self.object = PaymentProcess.objects.create()
        context = self.get_context(transactions)
        sepa = lxml.builder.ElementMaker(
             nsmap = {
                 'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                 None: 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03',
             }
        )
        sepa = sepa.Document(
            E.CstmrCdtTrfInitn(
                self._get_header(context),
                E.PmtInf(                                   # Payment Info
                    E.PmtInfId(str(self.object.id)),        # Payment Id
                    E.PmtMtd("TRF"),                        # Payment Method
                    E.NbOfTxs(context['num_transactions']), # Number of Transactions
                    E.CtrlSum(context['total']),            # Control Sum
                    E.ReqdExctnDt   (                       # Requested Execution Date
                        context['now'].strftime("%Y-%m-%d")
                    ),
                    E.Dbtr(                                 # Debtor
                        E.Nm(context['name'])
                    ),
                    E.DbtrAcct(                             # Debtor Account
                        E.Id(
                            E.IBAN(context['iban'])
                        )
                    ),
                    E.DbtrAgt(                              # Debtor Agent
                        E.FinInstnId(                       # Financial Institution Id
                            E.BIC(context['bic'])
                        )
                    ),
                *list(self._get_credit_transactions(transactions))   # Transactions
                )
            )
        )
        file_name = 'credit-transfer-%i.xml' % self.object.id
        self._process_xml(sepa, 'pain.001.001.03.xsd', file_name)
    
    def _process_debts(self, transactions):
        from ..models import PaymentProcess
        self.object = PaymentProcess.objects.create()
        context = self.get_context(transactions)
        sepa = lxml.builder.ElementMaker(
             nsmap = {
                 'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                 None: 'urn:iso:std:iso:20022:tech:xsd:pain.008.001.02',
             }
        )
        sepa = sepa.Document(
            E.CstmrDrctDbtInitn(
                self._get_header(context),
                E.PmtInf(                                   # Payment Info
                    E.PmtInfId(str(self.object.id)),        # Payment Id
                    E.PmtMtd("DD"),                         # Payment Method
                    E.NbOfTxs(context['num_transactions']), # Number of Transactions
                    E.CtrlSum(context['total']),            # Control Sum
                    E.PmtTpInf(                             # Payment Type Info
                        E.SvcLvl(                           # Service Level
                            E.Cd("SEPA")                    # Code
                        ),
                        E.LclInstrm(                        # Local Instrument
                            E.Cd("CORE")                    # Code
                        ),
                        E.SeqTp("RCUR")                     # Sequence Type
                    ),
                    E.ReqdColltnDt(                         # Requested Collection Date
                        context['now'].strftime("%Y-%m-%d")
                    ),
                    E.Cdtr(                                 # Creditor
                        E.Nm(context['name'])
                    ),
                    E.CdtrAcct(                             # Creditor Account
                        E.Id(
                            E.IBAN(context['iban'])
                        )
                    ),
                    E.CdtrAgt(                              # Creditor Agent
                        E.FinInstnId(                       # Financial Institution Id
                            E.BIC(context['bic'])
                        )
                    ),
                *list(self._get_debt_transactions(transactions))   # Transactions
                )
            )
        )
        file_name = 'direct-debit-%i.xml' % self.object.id
        self._process_xml(sepa, 'pain.008.001.02.xsd', file_name)
    
    def get_context(self, transactions):
        return {
            'name': settings.PAYMENTS_DD_CREDITOR_NAME,
            'iban': settings.PAYMENTS_DD_CREDITOR_IBAN,
            'bic': settings.PAYMENTS_DD_CREDITOR_BIC,
            'at02_id': settings.PAYMENTS_DD_CREDITOR_AT02_ID,
            'now': timezone.now(),
            'total': str(sum([abs(transaction.amount) for transaction in transactions])),
            'num_transactions': str(len(transactions)),
        }
    
    def _get_debt_transactions(self, transactions):
        for transaction in transactions:
            self.object.transactions.add(transaction)
            # TODO transaction.account
            account = transaction.bill.account
            # FIXME
            data = account.payment_sources.first().data
            transaction.state = transaction.WAITTING_CONFIRMATION
            transaction.save()
            yield E.DrctDbtTxInf(                           # Direct Debit Transaction Info
                E.PmtId(                                    # Payment Id
                    E.EndToEndId(str(transaction.id))       # Payment Id/End to End
                ),
                E.InstdAmt(                                 # Instructed Amount
                    str(abs(transaction.amount)),
                    Ccy=transaction.currency.upper()
                ),
                E.DrctDbtTx(                                # Direct Debit Transaction
                    E.MndtRltdInf(                          # Mandate Related Info
                        E.MndtId(str(account.id)),          # Mandate Id
                        E.DtOfSgntr(                        # Date of Signature
                            account.register_date.strftime("%Y-%m-%d")
                        )
                    )
                ),
                E.DbtrAgt(                                  # Debtor Agent
                    E.FinInstnId(                           # Financial Institution Id
                        E.Othr(
                            E.Id('NOTPROVIDED')
                        )
                    )
                ),
                E.Dbtr(                                     # Debtor
                    E.Nm(account.name),                     # Name
                ),
                E.DbtrAcct(                                 # Debtor Account
                    E.Id(
                        E.IBAN(data['iban'])
                    ),
                ),
            )
    
    def _get_credit_transactions(self, transactions):
        for transaction in transactions:
            self.object.transactions.add(transaction)
            # TODO transaction.account
            account = transaction.bill.account
            # FIXME
            data = account.payment_sources.first().data
            transaction.state = transaction.WAITTING_CONFIRMATION
            transaction.save()
            yield E.CdtTrfTxInf(                            # Credit Transfer Transaction Info
                E.PmtId(                                    # Payment Id
                    E.EndToEndId(str(transaction.id))       # Payment Id/End to End
                ),
                E.Amt(                                      # Amount
                    E.InstdAmt(                             # Instructed Amount
                        str(abs(transaction.amount)),
                        Ccy=transaction.currency.upper()
                    )
                ),
                E.CdtrAgt(                                  # Creditor Agent
                    E.FinInstnId(                           # Financial Institution Id
                        E.Othr(
                            E.Id('NOTPROVIDED')
                        )
                    )
                ),
                E.Cdtr(                                     # Debtor
                    E.Nm(account.name),                     # Name
                ),
                E.CdtrAcct(                                 # Creditor Account
                    E.Id(
                        E.IBAN(data['iban'])
                    ),
                ),
            )
    
    def _get_header(self, context):
        return E.GrpHdr(                            # Group Header
            E.MsgId(str(self.object.id)),           # Message Id
            E.CreDtTm(                              # Creation Date Time
                context['now'].strftime("%Y-%m-%dT%H:%M:%S")
            ),
            E.NbOfTxs(context['num_transactions']), # Number of Transactions
            E.CtrlSum(context['total']),            # Control Sum
            E.InitgPty(                             # Initiating Party
                E.Nm(context['name']),              # Name
                E.Id(                               # Identification
                    E.OrgId(                        # Organisation Id
                        E.Othr(
                            E.Id(context['at02_id'])
                        )
                    )
                )
            )
        )
    
    def _process_xml(self, sepa, xsd, file_name):
        # http://www.iso20022.org/documents/messages/1_0_version/pain/schemas/pain.008.001.02.zip
        path = os.path.dirname(os.path.realpath(__file__))
        xsd_path = os.path.join(path, xsd)
        schema_doc = etree.parse(xsd_path)
        schema = etree.XMLSchema(schema_doc)
        sepa = etree.parse(StringIO(etree.tostring(sepa)))
        schema.assertValid(sepa)
        self.object.file = file_name
        self.object.save()
        sepa.write(self.object.file.path,
                   pretty_print=True,
                   xml_declaration=True,
                   encoding='UTF-8')

