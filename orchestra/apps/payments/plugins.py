from djangoplugins.point import PluginPoint
import ast


class StandardInterpreter(object):

    def __init__(self, obj):
        data = ast.literal_eval(obj.data)
        for key in data.keys():
            exec "self.%s = data['%s']" % (key, key)


class PaymentMethod(PluginPoint):
    
    """ 
    Attributes:
        # Name of the plugin
        name = 'q19'
        
        # Description of the plugin
        title = 'q19 payment gateway'
        
        # Mimetype of the generated files on process()
        mimetype = 'text/plain'
        
        # Extention of the generated files on process()
        extention = 'q19'
        
    The plugins for this plugin point must provide the following methods:
        def get_transaction_data(self, buyer_data, seller_data, bill, id)
            which generates the custom transaction information stored on Transaction.data        
        
        def process(self, transactions):
            which processes the transaction
            optionally it can returns a cStringIO file to be downloaded
        
        def get_transaction_data(self, buyer_data, seller_data, bill, id):

        def data_validation(self, form, data_dict):
            validates the data field on contacacts payment details

    Override if needed:        
        def initial_state(self):

        def transaction_interpreter(self, transaction):
            which provides an interpretation for the Transaction.data field 

        def payment_details_interpreter(self, details):
            which provides an interpreter for PaymentDetail.data field

    Templates:
        plugin_name/templates/plugin_name_payment_comment.html {{ interpreted_data }} {{ bill}}

    """

    @property
    def initial_state(self):
        import settings
        return settings.DEFAULT_INITIAL_STATUS
        
    def transaction_interpreter(self, transaction):
        return StandardInterpreter(transaction)

    def payment_details_interpreter(self, details):
        return StandardInterpreter(details)        

