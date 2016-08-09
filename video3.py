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
import chardet
import chardet
import sys
import numpy as np
import cv2
from pylepton import Lepton
import io
import time
import picamera

class Data(object):
    def __init__(self):
        print "init"
        self.camera = picamera.PiCamera()

    def read(self):
         # Set the camera's resolution to VGA @40fps and give it a couple
        # of seconds to measure exposure etc.
        self.camera.resolution = (80, 60)
        self.camera.framerate = 80
        #time.sleep(2)
        # Set up 40 in-memory streams
        outputs = [io.BytesIO() for i in range(40)]
        start = time.time()
        self.camera.capture_sequence(outputs, 'jpeg', use_video_port=True)
        finish = time.time()
        print finish-start
        # How fast were we?
        return outputs[39].getvalue()
        
        


class ClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        print "server connected"
        self.my_data = Data()

    def onOpen(self):
        #Send message to server with client identity and type
        self.sendMessage('[{"proto":{"identity":"'+str(uuid.uuid1())+'","type":"vis_image"}}]')
        LoopingCall(self.sendBits).start(.5)

    def sendBits(self):
        image = base64.b64encode(self.my_data.read())
        packaged = json.dumps([{"vis_image" : image}])
        print len(packaged)
        self.sendMessage(packaged)
        print "sent"


if __name__ == '__main__':
    #Make a client factort that's directed at CSUITE
    factory = WebSocketClientFactory(u"ws://www.csuiteexperiment.com:9002")

    #Give the factory our protocol
    factory.protocol = ClientProtocol

    #Make a TCP connection to CSUITE
    reactor.connectTCP("www.csuiteexperiment.com", 9002, factory)
    reactor.run()
    cam.stop_recording()
    cam.close()
