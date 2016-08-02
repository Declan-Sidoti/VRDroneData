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

#tn = Telnet("192.168.10.123", 7060)
#print tn.write('-N')

time.time()
import urllib2
class Data(object):
    def __init__(self):
        self.my_bytes = b""
        self.response = urllib2.urlopen("http://192.168.10.123:7060")
    def read(self):
        #new_bytes= tn.read_eager()
        new_bytes= self.response.read(2048*16+64)
        #print (new_bytes)
        #with open("bytestream.bin","a") as of: of.write(new_bytes)
        self.my_bytes += new_bytes
        a = self.my_bytes.find(b"\xff\xd8")
        b = self.my_bytes.find(b"\xff\xd9")
        print a,b
        if a!=-1 and b!=-1 and b>a:
            print ("success")
            jpg = self.my_bytes[a:b+2]
            self.my_bytes = self.my_bytes[b+2:]
            end_data = base64.b64encode(jpg)
            return json.dumps([{"lieber" : end_data}])
        return

class ClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        self.data_class = Data()
        self.spinner = spinner()
        self.last_time = time.time()
    def onOpen(self):
        self.sendMessage('[{"proto":{"identity":"'+str(uuid.uuid1())+'","type":"lieber"}}]')
        print("server connection")
        LoopingCall(self.send).start(0.05)
    def onConnect(self, response):
        print "Server Connected: {0}:".format(response.peer)
    def send(self):
        self.spinner.update()
        my_msg = self.data_class.read()
        if my_msg is not None and time.time()-self.last_time > 0.4:
            self.last_time = time.time()
            print("###")
            self.sendMessage(my_msg.encode("utf-8"),isBinary =False)



class spinner(object):
    def __init__(self):
        self.state = 0
    def update(self):
        self.state+=1
        self.state%=2
        sys.stdout.write(["\r | ","\r-- "][self.state])
        sys.stdout.flush()

#d=Data()
#LoopingCall(d.read).start(0.5)
#Make a client factory that's directed at CSUITE
factory = WebSocketClientFactory(u"ws://54.187.114.157:9002")
factory.protocol = ClientProtocol
reactor.connectTCP("54.187.114.157", 9002, factory)
#54.187.114.157
print("running")
reactor.run()
