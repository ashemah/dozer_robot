from base_service import BaseService


class MasterService(BaseService):

    def __init__(self, node_name, launch_params, callback):
        super(MasterService, self).__init__(node_name, launch_params)
        self.callback = callback

    def on_service_message(self, sender, message):
        self.callback(sender, message)
