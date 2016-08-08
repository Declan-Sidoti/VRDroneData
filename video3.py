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

class Data(object):
    def __init__(self):
        print "init"

    def read(self):
        stream=io.BytesIO()
        with picamera.PiCamera() as camera:
            camera.resolution = (2592, 1944)
            camera.capture (stream, format='jpeg', bayer=True)
            return stream
        return


class ClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        self.my_data = Data()

    def onOpen(self):
        #Send message to server with client identity and type
        self.sendMessage('[{"proto":{"identity":"'+str(uuid.uuid1())+'","type":"vis_image"}}]')
        LoopingCall(self.sendBits).start(0.2)

    def sendBits(self, s):
        image = base64.b64encode(self.my_data.read())
        packaged = json.dumps([{"vis_image" : image}])
        self.sendMessage(packaged)


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
