from comms import Comms


class BaseNode(object):

    def __init__(self, params):
        self.params = params

        self.comms = Comms()
        self.message_bus = self.comms.get_message_bus()

    def get_param(self, name, default=None):

        if name in self.params:
            return self.params[name]
        else:
            return default

    def setup(self):
        pass

    def run(self):
        self.comms.process_messages()
