from contacts.models import Contact
from datetime import datetime 
from django import template
from payment import settings
from payment.plugins import PaymentMethod


class Q19(PaymentMethod):
    name = 'q19'
    title = 'q19 payment gateway'
    
    def process(self, transactions):
        q19 = self._generate_q19_first_procedure(transactions)
        return q19

    def _generate_q19_first_procedure(self, transactions):
        class Ordenante(object): pass
        
        transacciones_agrupadas = {}
        for transaction in transactions:
            key = transaction.interpreted_data.codigo_presentador
            if not key in transacciones_agrupadas.keys():
                transacciones_agrupadas[key] = [transaction]
            else:     
                transacciones_agrupadas[key].append(transaction)
        
        total = 0.00
        numero_de_domiciliaciones = 0
        numero_de_registros = 2
        numero_de_ordenantes = 0
        
        for key in transacciones_agrupadas.keys():
            o_total = 0.00
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
    
