import ast

def _get_q19_concept(bill):
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

    
def get_transaction_data(buyer_data, seller_data, bill, id):

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
            'conceptos': _get_q19_concept(bill),
            'codigo_de_referencia_interna': bill.ident}
    return data
        
