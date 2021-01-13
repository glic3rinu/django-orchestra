import datetime
import logging
import os
from io import StringIO

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_iban.validators import IBANValidator, IBAN_COUNTRY_CODE_LENGTH
from rest_framework import serializers

from orchestra.plugins.forms import PluginDataForm

from .. import settings
from .options import PaymentMethod


logger = logging.getLogger(__name__)

try:
    import lxml
except ImportError:
    logger.error('Error loading lxml, module not installed.')


class SEPADirectDebitForm(PluginDataForm):
    iban = forms.CharField(label='IBAN',
        widget=forms.TextInput(attrs={'size': '50'}))
    name = forms.CharField(max_length=128, label=_("Name"),
        widget=forms.TextInput(attrs={'size': '50'}))


class SEPADirectDebitSerializer(serializers.Serializer):
    iban = serializers.CharField(label='IBAN', validators=[IBANValidator()],
        min_length=min(IBAN_COUNTRY_CODE_LENGTH.values()), max_length=34)
    name = serializers.CharField(label=_("Name"), max_length=128)
    
    def validate(self, data):
        data['iban'] = data['iban'].strip()
        data['name'] = data['name'].strip()
        return data


class SEPADirectDebit(PaymentMethod):
    verbose_name = _("SEPA Direct Debit")
    label_field = 'name'
    number_field = 'iban'
    allow_recharge = True
    form = SEPADirectDebitForm
    serializer = SEPADirectDebitSerializer
    due_delta = datetime.timedelta(days=5)
    state_help = {
        'WAITTING_PROCESSING': _("The transaction is created and requires the generation of "
                                 "the SEPA direct debit XML file."),
        'WAITTING_EXECUTION': _("SEPA Direct Debit XML file is generated but needs to be sent "
                                "to the financial institution."),
    }
    
    def get_bill_message(self):
        context = {
            'number': self.instance.number
        }
        return settings.PAYMENTS_DD_BILL_MESSAGE % context
    
    @classmethod
    def process(cls, transactions):
        debts = []
        credits = []
        for transaction in transactions:
            if transaction.amount < 0:
                credits.append(transaction)
            else:
                debts.append(transaction)
        processes = []
        if debts:
            proc = cls.process_debts(debts)
            processes.append(proc)
        if credits:
            proc = cls.process_credits(credits)
            processes.append(proc)
        return processes
    
    @classmethod
    def process_credits(cls, transactions):
        import lxml.builder
        from lxml.builder import E
        from ..models import TransactionProcess
        process = TransactionProcess.objects.create()
        context = cls.get_context(transactions)
        # http://businessbanking.bankofireland.com/fs/doc/wysiwyg/b22440-mss130725-pain001-xml-file-structure-dec13.pdf
        sepa = lxml.builder.ElementMaker(
             nsmap = {
                 'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                 None: 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03',
             }
        )
        sepa = sepa.Document(
            E.CstmrCdtTrfInitn(
                cls.get_header(context, process),
                E.PmtInf(                                   # Payment Info
                    E.PmtInfId(str(process.id)),            # Payment Id
                    E.PmtMtd("TRF"),                        # Payment Method
                    E.NbOfTxs(context['num_transactions']), # Number of Transactions
                    E.CtrlSum(context['total']),            # Control Sum
                    E.ReqdExctnDt(                          # Requested Execution Date
                        (context['now']+datetime.timedelta(days=10)).strftime("%Y-%m-%d")
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
                *list(cls.get_credit_transactions(transactions, process))   # Transactions
                )
            )
        )
        file_name = 'credit-transfer-%i.xml' % process.id
        cls.process_xml(sepa, 'pain.001.001.03.xsd', file_name, process)
        return process
    
    @classmethod
    def process_debts(cls, transactions):
        import lxml.builder
        from lxml.builder import E
        from ..models import TransactionProcess
        process = TransactionProcess.objects.create()
        context = cls.get_context(transactions)
        # http://businessbanking.bankofireland.com/fs/doc/wysiwyg/sepa-direct-debit-pain-008-001-02-xml-file-structure-july-2013.pdf
        sepa = lxml.builder.ElementMaker(
             nsmap = {
                 'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                 None: 'urn:iso:std:iso:20022:tech:xsd:pain.008.001.02',
             }
        )
        sepa = sepa.Document(
            E.CstmrDrctDbtInitn(
                cls.get_header(context, process),
                E.PmtInf(                                   # Payment Info
                    E.PmtInfId(str(process.id)),            # Payment Id
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
                *list(cls.get_debt_transactions(transactions, process))   # Transactions
                )
            )
        )
        file_name = 'direct-debit-%i.xml' % process.id
        cls.process_xml(sepa, 'pain.008.001.02.xsd', file_name, process)
        return process
    
    @classmethod
    def get_context(cls, transactions):
        return {
            'name': settings.PAYMENTS_DD_CREDITOR_NAME,
            'iban': settings.PAYMENTS_DD_CREDITOR_IBAN,
            'bic': settings.PAYMENTS_DD_CREDITOR_BIC,
            'at02_id': settings.PAYMENTS_DD_CREDITOR_AT02_ID,
            'now': timezone.now(),
            'total': str(sum([abs(transaction.amount) for transaction in transactions])),
            'num_transactions': str(len(transactions)),
        }
    
    @classmethod
    def get_debt_transactions(cls, transactions, process):
        import lxml.builder
        from lxml.builder import E
        for transaction in transactions:
            transaction.process = process
            transaction.state = transaction.WAITTING_EXECUTION
            transaction.save(update_fields=('state', 'process', 'modified_at'))
            account = transaction.account
            data = transaction.source.data
            yield E.DrctDbtTxInf(                           # Direct Debit Transaction Info
                E.PmtId(                                    # Payment Id
                    E.EndToEndId(                           # Payment Id/End to End
                        str(transaction.bill.number)+'-'+str(transaction.id)
                    )
                ),
                E.InstdAmt(                                 # Instructed Amount
                    str(abs(transaction.amount)),
                    Ccy=transaction.currency.upper()
                ),
                E.DrctDbtTx(                                # Direct Debit Transaction
                    E.MndtRltdInf(                          # Mandate Related Info
                        # + 10000 xk vam canviar de sistema per generar aquestes IDs i volem evitar colisions amb els
                        #  numeros usats antigament
                        E.MndtId(str(transaction.source_id+10000)),          # Mandate Id
                        E.DtOfSgntr(                        # Date of Signature
                            account.date_joined.strftime("%Y-%m-%d")
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
                    E.Nm(account.billcontact.get_name()),         # Name
                ),
                E.DbtrAcct(                                 # Debtor Account
                    E.Id(
                        E.IBAN(data['iban'].replace(' ', ''))
                    ),
                ),
            )
    
    @classmethod
    def get_credit_transactions(cls, transactions, process):
        import lxml.builder
        from lxml.builder import E
        for transaction in transactions:
            transaction.process = process
            transaction.state = transaction.WAITTING_EXECUTION
            transaction.save(update_fields=('state', 'process', 'modified_at'))
            account = transaction.account
            data = transaction.source.data
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
                        E.IBAN(data['iban'].replace(' ', ''))
                    ),
                ),
            )
    
    @classmethod
    def get_header(cls, context, process):
        import lxml.builder
        from lxml.builder import E
        return E.GrpHdr(                            # Group Header
            E.MsgId(str(process.id)),           # Message Id
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
    
    @classmethod
    def process_xml(cls, sepa, xsd, file_name, process):
        from lxml import etree
        # http://www.iso20022.org/documents/messages/1_0_version/pain/schemas/pain.008.001.02.zip
        path = os.path.dirname(os.path.realpath(__file__))
        xsd_path = os.path.join(path, xsd)
        schema_doc = etree.parse(xsd_path)
        schema = etree.XMLSchema(schema_doc)
        sepa = StringIO(etree.tostring(sepa).decode('utf8'))
        sepa = etree.parse(sepa)
        schema.assertValid(sepa)
        process.file = file_name
        process.save(update_fields=['file'])
        sepa.write(process.file.path,
                   pretty_print=True,
                   xml_declaration=True,
                   encoding='UTF-8')
