import argparse
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import serial
import subprocess
import psutil

# parser = argparse.ArgumentParser(description='Process some integers.')
#
# parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
# parser.add_argument('--sum', dest='accumulate', action='store_const', const=sum, default=max,
#                     help='sum the integers (default: find the max)')
#
# args = parser.parse_args()


class DozerCore:

    def __init__(self, server_ip, server_port, serial_port, serial_port_speed):

        self.serial_port = serial.Serial(serial_port, serial_port_speed)

        self.server = SimpleJSONRPCServer((server_ip, server_port))
        self.server.register_function(self.move_fwd)
        self.server.register_function(self.move_back)
        self.server.register_function(self.rotate_left)
        self.server.register_function(self.rotate_right)
        self.server.register_function(self.stop)
        self.server.register_function(self.enable_camera)
        self.server.register_function(self.disable_camera)

        self.proc = None

    def move_fwd(self):
        self.serial_port.write('FWD0')

    def move_back(self):
        self.serial_port.write('BACK0')

    def rotate_left(self):
        self.serial_port.write('LEFT0')

    def rotate_right(self):
        self.serial_port.write('RIGHT0')

    def stop(self):
        self.serial_port.write('STOP0')

    def enable_camera(self):
        if self.proc is not None:
            self.proc.terminate()

        self.proc = subprocess.Popen(["/home/pi/dozer/video.sh"], stdout=subprocess.PIPE, shell=True)

    def disable_camera(self):

        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'cmdline'])
            except psutil.NoSuchProcess:
                pass
            else:
                print(pinfo)
                cmdstr = "".join(pinfo['cmdline'])
                if 'video.sh' in cmdstr:
                    print "KILLIN {}".format(pinfo['pid'])
                    parent = psutil.Process(pinfo['pid'])
                    for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                        child.kill()
                    parent.kill()

    def run(self):
        self.server.serve_forever()


if __name__ == '__main__':

    dozer_core = DozerCore('0.0.0.0', 8080, '/dev/ttyACM0', 9600)
    dozer_core.run()
