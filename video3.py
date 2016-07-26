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

camwrite = None
cam = None
class MyOutput():
    def write(self, s):
        camwrite(s)


class ClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        global cam, camwrite
        camwrite = self.sendBits
        cam = picamera.PiCamera()
        cam.framerate = 2
        cam.exposure_mode = 'night'
    
    def onOpen(self):
        #Send message to server with client identity and type
        self.sendMessage('[{"proto":{"identity":"'+str(uuid.uuid1())+'","type":"video_test"}}]')
        self.record()
    
    def sendBits(self, s):
        self.sendMessage('[{"video_stream":'+s.encode('base64')+'}]')
    
    
    def record(self):
        cam.start_recording(MyOutput(), format = 'h264', bitrate=0, quality = 40)
    #cam.wait_recording(1)
    #cam.stop_recording()
    
    def onMessage(self, payload, isBinary):
        
        if not isBinary:
            msg = "{} from {}".format(payload.decode('utf8'), self.peer)
            #self.factory.broadcast(msg)
            cmd = json.loads(payload)
        if(cmd.has_key("cmd")):
            if(cmd["cmd"]=="showPreview"):
                cam.start_preview()
            if(cmd["cmd"]=="hidePreview"):
                cam.stop_preview()
            if(cmd["cmd"]=="startRecord"):
                loopingCall = task.LoopingCall(self.record)
                loopingCall.start(1)
        
        
            if(cmd["cmd"]=="stopRecord"):
                cam.stop_recording()
                loopingCall.stop()
            
            if(cmd.has_key("framerate")):
            cam.stop_recording()
            cam.framerate=int(cmd["framerate"])
                    cam.start_recording(MyOutput(), format='h264',bitrate=0,quality=40)


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