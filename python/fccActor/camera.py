import numpy as np
import astropy.io.fits as pyfits
from time import localtime, strftime
import ac62kusb

class Camera(object):
	""" AC62KUSB Endoscope Camera module

	Parameters
		| exptime: sensor exposure time parameter(0-249)
		| gain: sensor adc gain parameter(0-3)

	"""

	def __init__(self, cmd, exptime, gain):
		""" Initialize the camera """

		self.exptime = exptime
		self.gain = gain
		self.camera = ac62kusb.Camera(exptime=exptime, gain=gain)
		cmd.inform('text="Camera initialized"')

	def setGain(self, cmd, gain):
		""" Set camera gain (0-3) """

		if gain<0 or gain>3:
			cmd.warn(f'text="Gain value is not valid(0-3): {gain}"')
			return
		self.camera.setGain(gain)
		self.gain = gain
		cmd.inform(f'text="Set gain to {gain}"')

	def setExptime(self, cmd, exptime):
		""" Set exposure time (0-249) """

		if exptime<0 or exptime>249:
			cmd.warn(f'text="Exposure time is not valid(0-249): {exptime}"')
			return
		self.camera.setExptime(exptime)
		self.exptime = exptime
		cmd.inform(f'text="Set exptime to {exptime}"')

	def expose(self, cmd, filename, frames):
		""" Expose and save image """

		if frames<1:
			cmd.warn(f'text="Frames value is not valid: {frames}"')
			return
		self.camera.expose(frames)
		cmd.inform('text="expose command succeed..."')

		hdu = pyfits.PrimaryHDU(self.camera.buffer)
		hdr = hdu.header
		hdr.set('DATE', strftime("%Y-%m-%dT%H:%M:%S", localtime()), 'file creation date (local)')
		hdr.set('INSTRUME', 'FCC', 'AC62KUSB Endoscope Camera')
		hdr.set('NFRAME', frames, 'number of frames')
		hdr.set('GAIN', self.gain, 'camera gain(0-3)')
		hdr.set('EXPTIME', self.exptime, 'expore time(0-249)')
		hdu.writeto(filename, checksum=True, overwrite=True)
		cmd.inform(f'text="write to fits file: filename={filename}"')

	def sendStatusKeys(self, cmd):
		""" Send our status keys to the given command. """ 

		cmd.inform('text="model=AC62KUSB Endoscope Camera"')
		cmd.inform(f'text="gain={self.gain}"')
		cmd.inform(f'text="exptime={self.exptime}"')
