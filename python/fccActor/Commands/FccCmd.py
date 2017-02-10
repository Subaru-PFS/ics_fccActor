#!/usr/bin/env python

import os

import opscore.protocols.keys as keys
import opscore.protocols.types as types
from opscore.utility.qstr import qstr

class FccCmd(object):

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
			('reconnect', '', self.reconnect),
			('expose', '<exptime>', self.expose),
			('setgain', '<gain>', self.setGain),
			('abort', '', self.abort),
		]

		# Define typed command arguments for the above commands.
		self.keys = keys.KeysDictionary("fcc_fcc", (1, 1),
										keys.Key("exptime", types.Float(), help="Exposure time(s)"),
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

	def reconnect(self, cmd):
		""" reconnect camera device """

		self.actor.connectCamera(cmd)
		cmd.finish('text="camera connected!"')

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
		""" Take an exposure with multiple frames. """

		exptime = cmd.cmd.keywords['exptime'].values[0]
		filename = self._getNextFilename(cmd)
		self.actor.camera.expose(cmd, exptime, filename)

		#cmd.finish()

	def setGain(self, cmd):
		""" Set gain in db """

		gain = cmd.cmd.keywords['gain'].values[0]
		self.actor.camera.set_gain(cmd, gain)
		cmd.finish()

	def abort(self, cmd):
		""" Abort current exposure """

		self.actor.camera.cancel(cmd)
		cmd.finish()
