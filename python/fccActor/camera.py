import socket
import thread
import numpy as np
import astropy.io.fits as pyfits
from struct import *
from time import localtime, strftime

class Camera(object):
	""" Client for AWAIBA camera server

	Commmands to server
		EXP123: expose for 12.3s
		GAIN01: set gain to 1
		CANCEL: cancel exposure
		STATUS: query camera status

	Response from server
		NC:	not connected
		BP: bad parameter
		FL: fail
		BU: camera busy
		RE: camera ready
		OK: command received

	Binary image data from server
		int32	width
		int32	height
		int32	total frames
		double	data[250 * 250]

	"""

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((host, port))
		self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock2.connect((host, port+1))
		self.buffer = bytearray(250*250*8*2)
		self.data_available = False
		self.gain = 2

	def close_connection(self):
		self.sock.close()
		self.sock2.close()

	def reconnect(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.host, self.port))
		self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock2.connect((self.host, self.port+1))

	def set_gain(self, cmd, gain):
		if(gain<0 or gain>3):
			return "BP\n"
		self.sock.send("GAIN0"+str(gain))
		self.gain = gain
		cmd.inform('text="Set gain to %d: %s"' % (gain, self.sock.recv(16)))

	def expose(self, cmd, exp_time, filename):
		self.data_available = False
		self.exp_time = exp_time
		if(exp_time<0 or exp_time>=100):
			cmd.inform('text="Bad exposure parameter: %f"' % (exp_time))
		self.sock.send("EXP"+str(int(exp_time*10)).zfill(3))
		thread.start_new_thread(self._get_data, (cmd, filename,))
		cmd.inform('text="Send expose command: %s"' % (self.sock.recv(16)))

	def cancel(self, cmd):
		self.sock.send("CANCEL")
		cmd.inform('text="Abort exposure %s"' % (self.sock.recv(16)))

	def status(self):
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
		cmd.inform('status="%s"' % (self.status()))
