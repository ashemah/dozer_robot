from base_node import BaseNode
from service_link import ServiceServer


class BaseService(BaseNode):

    def __init__(self, params):
        super(BaseService, self).__init__(params)
        self.service_host = ServiceServer(params['service_port'], self.on_service_message)
        self.comms.add_module(self.service_host)

    def on_service_message(self, sender, message):
        print "asdsadsad"
