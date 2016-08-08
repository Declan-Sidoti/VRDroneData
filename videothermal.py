import sys
import json
import uuid
import base64
from time import sleep
import picamera,threading
from twisted.internet.task import LoopingCall,deferLater
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from fractions import Fraction
from twisted.web.static import File
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, listenWS
from pylepton import Lepton
import chardet

class ClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        global image
        self.image = None

    def onOpen(self):
        #Send message to server with client identity and type
        self.sendMessage('[{"proto":{"identity":"'+str(uuid.uuid1())+'","type":"thermal_image"}}]')

    def sendThermal(self):
        self.sendMessage(image)
        print image
    def capture():
          flip_v = False
          device = "/dev/spidev0.0"
          with Lepton(device) as l:
                a,_ = l.capture()
          if flip_v:
                cv2.flip(a,0,a)
          cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
          np.right_shift(a, 8, a)
          return np.uint8(a)

    def onMessage(self, payload, isBinary):
        if isBinary:
            print "Binary Message"
        else
            self.digest(payload)

    def digest(self, payload):
        try:
            payload=json.loads(payload)
            if 'capture' in payload:
                image = capture()
        except Exception, e:
            print "Payload not JSON formatted string"
            print e


if __name__ == '__main__':
    #Make a client factort that's directed at CSUITE
    factory = WebSocketClientFactory(u"ws://www.csuiteexperiment.com:9002")

    #Give the factory our protocol
    factory.protocol = ClientProtocol

    #Make a TCP connection to CSUITE
    reactor.connectTCP("www.csuiteexperiment.com", 9002, factory)

    reactor.run()
