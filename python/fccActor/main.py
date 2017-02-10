#!/usr/bin/env python

import actorcore.Actor
import camera

class Fcc(actorcore.Actor.Actor):
    def __init__(self, name, productName=None, configFile=None, debugLevel=30):
        # This sets up the connections to/from the hub, the logger, and the twisted reactor.
        #
        actorcore.Actor.Actor.__init__(self, name, 
                                       productName=productName, 
                                       configFile=configFile)
        # We will actually use a allocator with "global" sequencing
        self.exposureID = 0
        self.host = self.config.get('fcc', 'camHost')
        self.port = int(self.config.get('fcc', 'camPort'))

        self.connectCamera(self.bcast)

    def connectCamera(self, cmd, doFinish=True):
        reload(camera)
        self.camera = camera.Camera(host=self.host, port=self.port)
        self.camera.sendStatusKeys(cmd)

#
# To work

def main():
    fcc = Fcc('fcc', productName='fccActor')
    fcc.run()

if __name__ == '__main__':
    main()
