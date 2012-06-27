import ast
from contacts.models import Contact
import cStringIO as StringIO
from datetime import datetime 
from decimal import Decimal
from django import template, forms
from django.utils.translation import ugettext as _
from payment import settings
from payment.plugins import PaymentMethod


class CCC(object):
    numero = None

    def __init__(self, numero):
        self.numero = numero

    def __unicode__(self):
        return str(numero)

    @property
    def entidad(self):
        return self.numero[:4]
        
    @property
    def oficina(self):
        return self.numero[4:8]

    
    @property
    def control(self):
        return self.numero[8:9]
    
    @property
    def cuenta(self):
        return self.numero[9:]


class PaymentDetailInterpreter(object):
    def __init__(self, payment_details):
        data = ast.literal_eval(payment_details.data)
        self.ccc = CCC(data['ccc'])
        if 'codigo_de_referencia' in data.keys():
            self.codigo_de_referencia = data['codigo_de_referencia']
        if 'sufijo' in data.keys():
            self.sufijo = data['sufijo']
        
    @property
    def codigo_presentador(self):
        return 


Q19_REJECTED_CHOICES = (
    (0, _(u'Importe a cero')),
    (1, _(u'Incorriente')),
    (2, _(u'No domiciliado')),
    (3, _(u'Oficina domiciliataria inexistente')),        
    (4, _(u'Aplicacion R.D. 338/90, sobre NIF')),
    (5, _(u'Por orden del cliente: error de domiciliacion')),
    (6, _(u'Por orden del cliente: disconformidad con el importe')),
    (7, _(u'Sin utilizar')),
    (8, _(u'Importe superior al limite. En los que intervengan no residentes')),
)


class Q19(PaymentMethod):
    name = 'q19'
    title = 'q19 payment gateway'
    mimetype = 'text/plain'
    extention = 'rec'
    
    def payment_details_interpreter(self, details):
        return PaymentDetailInterpreter(details)        

    def process(self, transactions):
        q19 = self._generate_q19_first_procedure(transactions)
        return StringIO.StringIO(q19.encode("UTF-8"))

    def get_transaction_data(self, buyer_data, seller_data, bill, id):
        data = {'codigo_presentador': "%s%s" % (bill.seller.national_id, seller_data.sufijo),
                'codigo_ordenante': "%s%s" % (bill.seller.national_id, seller_data.sufijo),
                'codigo_de_referencia': buyer_data.codigo_de_referencia,
                'nombre_del_cliente_presentador': bill.seller.name,
                'nombre_del_cliente_ordenante': bill.seller.name,
                'nombre_del_titular_de_la_domiciliacion': bill.buyer.name,
                'entidad_receptora': seller_data.ccc.entidad,
                'oficina_receptora': seller_data.ccc.oficina,
                'ccc_de_abono': seller_data.ccc.numero,
                'ccc_de_adeudo': buyer_data.ccc.numero,
                'codigo_para_devoluciones': id,
                'conceptos': self._get_q19_concept(bill),
                'codigo_de_referencia_interna': bill.ident}
        return data


    def data_validation(form):
        required_fields = ('ccc', 'codigo_de_referencia', 'sufijo')


    def clean_data(self, form, data_dict):
        #TODO: clean account with control digits 
        missing = ""
        for field in ('ccc', 'codigo_de_referencia', 'sufijo'):
            if field not in data_dict.keys():
                missing += " '%s', " % field
        if missing:
            raise forms.ValidationError("Please provide %s data." % missing[:-2])


    def _generate_q19_first_procedure(self, transactions):
        class Ordenante(object): pass
        
        transacciones_agrupadas = {}
        for transaction in transactions:
            key = transaction.interpreted_data.codigo_presentador
            if not key in transacciones_agrupadas.keys():
                transacciones_agrupadas[key] = [transaction]
            else:     
                transacciones_agrupadas[key].append(transaction)
        
        total = Decimal("0.00")
        numero_de_domiciliaciones = 0
        numero_de_registros = 2
        numero_de_ordenantes = 0
        
        for key in transacciones_agrupadas.keys():
            o_total = Decimal("0.00")
            num_transactions = 0
            num_concepts = 0
            
            for transaction in transacciones_agrupadas[key]:
                o_total += transaction.total
                num_transactions += 1
                num_concepts += len(transaction.interpreted_data.conceptos[1])
                
            ordenante = Ordenante()
            ordenante.total = o_total
            ordenante.numero_de_domiciliaciones = num_transactions     
            ordenante.numero_de_registros = num_transactions + num_concepts + 2
            ordenante.codigo_ordenante = key
            ordenante.nombre_del_cliente_ordenante = transaction.interpreted_data.nombre_del_cliente_ordenante
            ordenante.ccc_de_abono = transaction.interpreted_data.ccc_de_abono
            transacciones_agrupadas[ordenante] = transacciones_agrupadas.pop(key)
            
            total += o_total
            numero_de_domiciliaciones += num_transactions
            numero_de_registros += ordenante.numero_de_registros
            numero_de_ordenantes += 1
        
        #TODO: codigo presentador != codigo_ordenante solve it befor production!!! 
        #       same for nombre_del_cliente_presentador, entidad_receptora, oficina_receptora
        context_dict = {'codigo_presentador': ordenante.codigo_ordenante,
                        'nombre_del_cliente_presentador': ordenante.nombre_del_cliente_ordenante,
                        'entidad_receptora': transaction.interpreted_data.entidad_receptora,
                        'oficina_receptora': transaction.interpreted_data.oficina_receptora,
                        'fecha_confeccion': datetime.now().strftime("%d%m%y"),
                        'fecha_de_cargo': datetime.now().strftime("%d%m%y"),
                        'procedimiento': '01',
                        'transacciones_agrupadas': transacciones_agrupadas,
                        'total': total,
                        'numero_de_domiciliaciones': numero_de_domiciliaciones,
                        'numero_de_registros': numero_de_registros,
                        'numero_de_ordenantes': numero_de_ordenantes}
                        
        context = template.Context(context_dict)
        q19 = template.loader.get_template('first_procedure.q19').render(context)
        return q19
        
    def _get_q19_concept(self, bill):
        """ 8 lineas de 80 caracteres repartides en 16 campos de 40 caracteres
            distribuidos: [o, [[o, o, o], [o, o, o]]] """
        concepts = ""
        for line in bill.lines.all():
            concepts += "%s, " % (line.description)

        if concepts: 
            concepts = concepts[:-2]
        else: 
            return ['',[]]

        def split(string):
            ini = 0
            end = 0
            len_string = len(string)
            while end < len_string or ini > 639:
                end += 40 if len_string > (end+40) else len_string
                yield string[ini:end]
                ini = end

        counter = 2
        final_concept = []
        
        for pice in split(concepts):
            if counter == 2:
                if final_concept:
                    final_concept[1].append([pice])
                else: 
                    final_concept = [pice]
                    final_concept.append([[]])
                counter = 0
                
            else:
                final_concept[1][-1].append(pice)
                counter += 1
        
        if not final_concept[-1][0]:
            return final_concept
        
        while 3 > counter > 0:
            final_concept[1][-1].append('')
            counter += 1
            
        return final_concept




