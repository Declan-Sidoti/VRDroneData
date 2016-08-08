
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
import sys
import numpy as np
import cv2
from pylepton import Lepton
import io
import time
import picamera


stream=io.BytesIO()
camera = picamera.PiCamera()
camera.resolution = (2592, 1944)
camera.capture("image", format='jpeg', bayer=True)
print format(stream.seek(0,2),',d')
