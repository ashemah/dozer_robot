from base_service import BaseService
from serial_link import SerialLink


class HardwareService(BaseService):

    def __init__(self, namespace, node_name, launch_params):
        super(HardwareService, self).__init__(namespace, node_name, launch_params)

        self.is_open = False

        try:
            self.serial_link = SerialLink(self.get_param('serial_port'), self.get_param('serial_port_speed', 9600), self.get_param('stub'))
            self.serial_link.open()
            self.is_open = True
        except Exception, e:
            self.is_open = False

    def on_service_message(self, sender, message):

        cmd = message['cmd']

        if cmd == 'fwd':
            self.serial_link.write('FWD\n')
        elif cmd == 'back':
            self.serial_link.write('BACK\n')
        elif cmd == 'left':
            self.serial_link.write('LEFT\n')
        elif cmd == 'right':
            self.serial_link.write('RIGHT\n')
        elif cmd == 'stop':
            self.serial_link.write('STOP\n')
        elif cmd == 'move_head':
            position = message['position']
            self.serial_link.write('HEADPOS,' + str(position) + '\n')


