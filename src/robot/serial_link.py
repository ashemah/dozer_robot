import serial


class SerialLink(object):

    def __init__(self, name, speed, stub=False):
        self.stub = stub

        if not self.stub:
            self.serial_port = serial.Serial(name, speed)

    def open(self):
        print "Opening serial port"

        # if not self.stub:
        #     self.serial_port.open()

    def write(self, data):
        print "Serial: " + data

        if not self.stub:
            self.serial_port.write(data)
