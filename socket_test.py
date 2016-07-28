import socket
from telnetlib import Telnet
import base64, pickle
from twisted.internet import reactor, protocol, task
from autobahn.twisted.websocket import WebSocketClientProtocol
from twisted.python import log
from twisted.internet.task import LoopingCall,deferLater
from autobahn.twisted.websocket import WebSocketClientFactory
import sys
import json
import uuid
import time
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print "Socket successfully created"
except socket.error as err:
    print "socket creation failed with error %s" %(err)

tn = Telnet("192.168.10.123", 7060)
print "connected"
#print tn.write('-N')

time.time()

class Data:
    def __init__(self):
        self.my_bytes = b""
    def read(self):
        self.my_bytes += tn.read_eager()
        a = self.my_bytes.find(b"\xff\xd8")
        b = self.my_bytes.find(b"\xff\xd9")
        if a!=-1 and b!=-1:
            jpg = self.my_bytes[a:b+2]
            self.my_bytes = self.my_bytes[b+2:]
        end_data = base64.b64encode(self.my_bytes)
        print 1
        return pickle.dumps([{"lieber" : end_data}])

class ClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        print "init"
        self.data = Data()
    def onOpen(self):
        self.sendMessage('[{"proto":{"identity":"'+str(uuid.uuid1())+'","type":"lieber"}}]')
        LoopingCall(send).start(0.01)
    def onConnect(self, response):
        print "Server Connected: {0}:".format(response.peer)
    def send():
        print("sending")
        self.sendMessage(self.data.read())
        self.senMessage(time.time())

#d=Data()
#LoopingCall(d.read).start(0.5)
#Make a client factory that's directed at CSUITE
factory = WebSocketClientFactory(u"ws://54.187.114.157:9002")
factory.protocol = ClientProtocol
print("server connection")
reactor.connectTCP("54.187.114.157", 9002, factory)
#54.187.114.157
print("running")
reactor.run()
