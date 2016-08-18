from random import randint

class Serial():

    def read(self):
        return "B8"

    def write(self):
        return randint(0, 9)


class SerialException(Exception):
    def __init__(self, message, errors):
        
        # Call the base class constructor with the parameters it needs
        super(ValidationError, self).__init__(message)
        
        # Now for your custom code...
        self.errors = errors

