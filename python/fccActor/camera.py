import socket
import thread
import numpy as np
import astropy.io.fits as pyfits
from struct import *
from time import localtime, strftime

class Camera(object):
	""" Client for AWAIBA camera server

	Commands to server
		| EXP123: expose for 12.3s
		| GAIN01: set gain to 1
		| CANCEL: cancel exposure
		| STATUS: query camera status

	Response from server
		| NC: not connected
		| BP: bad parameter
		| FL: fail
		| BU: camera busy
		| RE: camera ready
		| OK: command received

	Binary image data from server
		| int32: width
		| int32: height
		| int32: total frames
		| double[250*250]: data

	Parameters
		| host: camera server host IP
		| port: TCP port number, there are two TCP connections.
                |	<port> is for command and response
                |	<port + 1> is for data transfer.
	"""

	def __init__(self, host, port):
		""" Initialize and make connection to MPS """
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((host, port))
		self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock2.connect((host, port+1))
		self.buffer = bytearray(250*250*8*2)
		self.data_available = False
		self.camera_busy=False
		self.gain = 2

	def close_connection(self):
		""" Close connection """
		self.sock.close()
		self.sock2.close()

	def reconnect(self):
		""" Re-connect to MPS """
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host, self.port))
		self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock2.connect((self.host, self.port+1))

	def set_gain(self, cmd, gain):
		""" Set camera gain (0-3) """
		if self.camera_busy:
			cmd.error('text="Camera is busy"')
			return
		if(gain<0 or gain>3):
			cmd.error('text="Gain value is not valid(0-3): %d"' % gain)
			return
		self.sock.send("GAIN0"+str(gain))
		self.gain = gain
		cmd.inform('text="Set gain to %d: %s"' % (gain, self.sock.recv(16)))

	def expose(self, cmd, exp_time, filename):
		""" Expose and save image """
		if self.camera_busy:
			cmd.fail('text="Camera is busy"')
			return
		if(exp_time<0 or exp_time>=100):
			cmd.fail('text="Bad exposure parameter: %f"' % (exp_time))
			return
		self.data_available = False
		self.camera_busy=True
		self.exp_time = exp_time
		self.sock.send("EXP"+str(int(exp_time*10)).zfill(3))
		thread.start_new_thread(self._get_data, (cmd, filename,))
		cmd.inform('text="Send expose command: %s"' % (self.sock.recv(16)))

	def cancel(self, cmd):
		""" Cancel exposure """
		if not self.camera_busy:
			cmd.error('text="Camera is not busy"')
			return
		self.sock.send("CANCEL")
		cmd.inform('text="Abort exposure: %s"' % (self.sock.recv(16)))

	def status(self):
		""" Report current status """
		if self.camera_busy:
			return "BU"
		self.sock.send("STATUS")
		return self.sock.recv(16)

	def _get_data(self, cmd, filename):
		(self.width, ) = unpack_from('<I', self.sock2.recv(calcsize('I')))
		(self.height, ) = unpack_from('<I', self.sock2.recv(calcsize('I')))
		(self.nframes, ) = unpack_from('<I', self.sock2.recv(calcsize('I')))
		left = self.width * self.height * calcsize('d')
		mview = memoryview(self.buffer)
		while left:
			nbytes = self.sock2.recv_into(mview, left)
			mview = mview[nbytes:]
			left -= nbytes
		fmt = "<%dd" % (self.width * self.height)
		self.data = np.asarray(unpack_from(fmt, self.buffer))
		self.data.shape = (self.width, self.height)
		self.data_available = True
		self.camera_busy=False
		self._wfits(cmd, filename)

	def _wfits(self, cmd, filename):
		"""Write image to a FITS file"""

		if(not self.data_available):
			return
		hdu = pyfits.PrimaryHDU(self.data)
		hdr = hdu.header
		hdr.update('DATE', strftime("%Y-%m-%dT%H:%M:%S", localtime()), 'file creation date (local)')
		hdr.update('INSTRUME', 'AWAIBA NanEye', 'instrument used to acquire image')
		hdr.update('NFRAME', self.nframes, 'number of frames')
		hdr.update('GAIN', self.gain, 'gain setting')
		hdu.writeto(filename, checksum=True, clobber=True)
		cmd.inform('text="Exposure complete, filename=%s"' % (filename))
		cmd.finish()

	def sendStatusKeys(self, cmd):
		""" Send our status keys to the given command. """ 

		cmd.inform('model="AWAIBA NanEye"')
		state = {
			"NC": "not connected",
			"FL": "fail",
			"BU": "camera busy",
			"RE": "camera ready"
                }[self.status()[:2]]
		cmd.inform('status="%s"' % (state))

