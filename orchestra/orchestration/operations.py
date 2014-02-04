class Operation(object):
    """
    Encapsulates an operation,
    storing its related object, the action and the backend.
    """
    def __init__(self, backend, instance, action):
        self.backend = backend
        self.instance = instance
        self.action = action
    
    def __hash__(self):
        return hash(self.backend) + hash(self.instance) + hash(self.action)
    
    def __eq__(self, operation):
        return hash(self) == hash(operation)

