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
import cv2
import sys
import numpy as np
import cv2
from pylepton import Lepton


class Data(object):
    def __init__(self):
        print "test"
   
    def capture(self):
          print "capturing"
          flip_v = False
          device = "/dev/spidev0.0"
          with Lepton(device) as l:
                a,_ = l.capture()
          if flip_v:
                cv2.flip(a,0,a)
          cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
          np.right_shift(a, 8, a)
          return np.uint8(a)
        


class ClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        self.image = None
        self.data_class = Data()
    def onOpen(self):
        #Send message to server with client identity and type
        self.sendMessage('[{"proto":{"identity":"'+str(uuid.uuid1())+'","type":"ir_cam"}}]')
        LoopingCall(self.sendThermal).start(.5)
    def sendThermal(self):
        image = self.data_class.capture()
        image = base64.b64encode(image)
        print image
        self.sendMessage(json.dumps({image}))
        

if __name__ == '__main__':
    #Make a client factort that's directed at CSUITE
    factory = WebSocketClientFactory(u"ws://www.csuiteexperiment.com:9002")

    #Give the factory our protocol
    factory.protocol = ClientProtocol

    #Make a TCP connection to CSUITE
    reactor.connectTCP("www.csuiteexperiment.com", 9002, factory)

    reactor.run()
