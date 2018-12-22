#!/usr/bin/env python

import os

import opscore.protocols.keys as keys
import opscore.protocols.types as types
from opscore.utility.qstr import qstr

class FccCmd(object):
	""" *Commmand Interface for MHS*

	Command list
		| ping
		| status
		| expose [frames=<int>]
		| setgain gain=<int: 0-3>
		| setexptime exptime=<int: 0-249>
		| abort

	 """

	def __init__(self, actor):
		# This lets us access the rest of the actor.
		self.actor = actor

		# Declare the commands we implement. When the actor is started
		# these are registered with the parser, which will call the
		# associated methods when matched. The callbacks will be
		# passed a single argument, the parsed and typed command.
		#
		self.vocab = [
			('ping', '', self.ping),
			('status', '', self.status),
			('expose', '[<frames>]', self.expose),
			('setexptime', '[<exptime>]', self.setExptime),
			('setgain', '[<gain>]', self.setGain),
		]

		# Define typed command arguments for the above commands.
		self.keys = keys.KeysDictionary("fcc_fcc", (1, 2),
			keys.Key("frames", types.Int(), help="Number of frames"),
			keys.Key("exptime", types.Int(), help="Exposure time(0-249)"),
			keys.Key("gain", types.Int(), help="Gain setting(0-3)"),
			)

	def ping(self, cmd):
		"""Query the actor for liveness/happiness."""

		cmd.finish("text='I am FCC actor'")

	def status(self, cmd):
		"""Report camera status and actor version. """

		self.actor.sendVersionKey(cmd)
		
		self.actor.camera.sendStatusKeys(cmd)
		cmd.inform('text="Present!"')
		cmd.finish()

	def _getNextFilename(self, cmd):
		""" Fetch next image filename. 

		In real life, we will instantiate a Subaru-compliant image pathname generating object.  

		"""
		
		self.actor.exposureID += 1
		path = os.path.join("$ICS_MHS_DATA_ROOT", 'fcc')
		path = os.path.expandvars(os.path.expanduser(path))

		if not os.path.isdir(path):
			os.makedirs(path, 0o755)
			
		return os.path.join(path, 'FCC%06d.fits' % (self.actor.exposureID))

	def expose(self, cmd):
		""" Take exposures with a number of frames

		This comand asks the AC62KUSB video camera to capture images for a number of frames.
		It then adds all the frames together and save it as a FITS file

		"""

		cmdKeys = cmd.cmd.keywords
		if 'frames' in cmdKeys:
			frames = cmd.cmd.keywords['frames'].values[0]
		else:
			frames = 1
		filename = self._getNextFilename(cmd)
		self.actor.camera.expose(cmd, filename, frames)
		cmd.finish()

	def setExptime(self, cmd):
		""" Set camera gain (0-3), the default value is 240 """

		cmdKeys = cmd.cmd.keywords
		if 'exptime' in cmdKeys:
			exptime = cmdKeys['exptime'].values[0]
		else:
			exptime = self.actor.exptime
		self.actor.camera.setExptime(cmd, exptime)
		cmd.finish()

	def setGain(self, cmd):
		""" Set camera gain (0-3), the default value is 0 """

		cmdKeys = cmd.cmd.keywords
		if 'gain' in cmdKeys:
			gain = cmd.cmd.keywords['gain'].values[0]
		else:
			gain = self.actor.gain
		self.actor.camera.setGain(cmd, gain)
		cmd.finish()
