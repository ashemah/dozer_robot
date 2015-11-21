from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import serial
import subprocess
import psutil

proc = None
ser = serial.Serial('/dev/ttyACM0', 9600)

def move_fwd():
	ser.write('FWD0')

def move_back():
	ser.write('BACK0')

def rotate_left():
	ser.write('LEFT0')

def rotate_right():
	ser.write('RIGHT0')

def stop():
	ser.write('STOP0')

def enable_camera():
	global proc
	if proc is not None:
		proc.terminate()

	proc = subprocess.Popen(["/home/pi/dozer/video.sh"], stdout=subprocess.PIPE, shell=True)	

def disable_camera():

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

server = SimpleJSONRPCServer(('0.0.0.0', 8080))
server.register_function(move_fwd)
server.register_function(move_back)
server.register_function(rotate_left)
server.register_function(rotate_right)
server.register_function(stop)
server.register_function(enable_camera)
server.register_function(disable_camera)
server.serve_forever()
