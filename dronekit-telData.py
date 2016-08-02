
#[{'uas_telemetry': {'autopilot_firmware_versions': <dronekit.Version object at 0x74d440b0>, 'battery': <dronekit.Battery object at 0x74d44170>, 'groundspeed': 0.0, 'is_armable': False, 'vx': 0.0, 'vy': -0.01, 'vz': 0.01, 'last_heartbeat': 0.32922209499997734, 'armed': True, 'velocity:': [0.0, -0.01, 0.01], 'airspeed': 0.0, 'global_location_relative_altitude': <dronekit.LocationGlobalRelative object at 0x74d44110>, 'gps': <dronekit.GPSInfo object at 0x74d44070>, 'ekf_ok': False, 'global_location': <dronekit.LocationGlobal object at 0x74d440f0>, 'rangefinder': <dronekit.Rangefinder object at 0x74d44190>, 'gimbal_status': <dronekit.Gimbal object at 0x75581270>, 'attitude:': <dronekit.Attitude object at 0x74d44150>, 'system_status': 'STANDBY', 'mode': 'STABILIZE', 'local_location': <dronekit.LocationLocal object at 0x74d44130>, 'heading': 10}}]
#

# Import DroneKit-Python

# Import DroneKit-Python

from dronekit import connect, VehicleMode
from twisted.internet import reactor, protocol, task
from autobahn.twisted.websocket import WebSocketClientProtocol
from twisted.python import log
from twisted.internet.task import LoopingCall,deferLater
from autobahn.twisted.websocket import WebSocketClientFactory
import sys
import json
import uuid
v = connect('/dev/ttyAMA0', baud=57600)

#class
class Data:
    #update
    def update(self):
        print 1
        cur_data = {
                                "uas_telemetry":{
                                "gps": v.gps_0,
                                "gps_fixtype":v.gps_0.fix_type,
                                #"battery": v.battery,
                                #"autopilot_firmware_versions": v.version,
                                #"autopilot_capabilities": v.capabilities.ftp,

                                #"local_location": v.location.local_frame
                                "velocity:": v.velocity,
                                "groundspeed": v.groundspeed,
                                "airspeed": v.airspeed,
                                #"gimbal_status": v.gimbal,
                                "battery_voltage": v.battery.voltage,
                                #"ekf_ok": v.ekf_ok,
                                "last_heartbeat": v.last_heartbeat,
                                #"rangefinder": v.rangefinder,
                                #"rangefinder_distance": v.rangefinder_distance,
                                #"rangefinder_voltage": v.rangefinder_voltage,
                                "heading": v.heading,
                                "is_armable": v.is_armable,
                                "system_status": v.system_status.state,
                                "mode": v.mode.name,
                                "armed": v.armed,
				"vx": v._vx,
				"vy": v._vy,
				"vz": v._vz
                                }
                    }
        if cur_data['uas_telemetry']['gps_fixtype']==3:#0:no,1:2d,3:3d
            cur_data['uas_telemetry']['gps_lat']= v.location.global_frame.lat
            cur_data['uas_telemetry']['gps_lon']= v.location.global_frame.lon
            cur_data['uas_telemetry']['gps_global_alt']=v.location.global_frame.alt
            cur_data['uas_telemetry']['gps_local_alt']=v.location.global_relative_frame.alt


            cur_data['uas_telemetry']['pitch']=v.attitude.pitch
            cur_data['uas_telemetry']['yaw']=v.attitude.yaw
            cur_data['uas_telemetry']['roll']=v.attitude.roll
        return json.dumps([cur_data])
  

class ClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        self.telData = Data()
	self.cmds = v.commands
	self.cmds.download()
    #What to do once the socket is open
    def onOpen(self):
        print 2
        #Send message to server with client identity and type
        self.sendMessage('[{"proto":{"identity":"'+str(uuid.uuid1())+'","type":"uav"}}]')
        LoopingCall(self.sendTelData).start(.05)
    #sends telemetry data from the pixhawk to the server
    def sendTelData(self):
        self.sendMessage(self.telData.update())
    #What to do once the server is connected to the client
    def onConnect(self, response):
        print "Server Connected: {0}:".format(response.peer)
    #when the client gets a message from the server it calls digest with the payload
    def onMessage(self, payload, isBinary):
        if isBinary:
            print "Binary Message"
        else:
            self.digest(payload)
    #loads the json and gives commands to the drone through dronekit
    def digest(self, payload):
        try:
            payload = json.loads(payload)
	#go to lat long and alt
            if 'simple_goto' in payload:
                (lat ,lon, alt) = payload.get('simple_goto')
                a_location = LocationGlobal(lat,lon,alt)
                v.simple_goto(a_location)
                print "go to lat,lon,alt"
	#add waypoints
           # elif 'add_waypoint' in payload:
            #    (lat, lon, alt) = payload.get('add_waypoint')
	#	cmd = Command(0,0,0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
   	#	 0, 0, 0, 0, 0, 0,
    	#	lat, lon, altitude)
	#	self.cmds.add(cmd)
	#	self.cmds.upload()
	#clear waypoints
	 #   elif 'clear_waypoints' in payload:
	#	self.cmds.clear()
         #       print "cleared waypoints"
          #  else: print ["No implementation for this payload:y"]+payload.keys()
        except Exception, e:
            print "Payload not JSON formatted string"
            print e


factory = WebSocketClientFactory(u"ws://www.csuiteexperiment.com:9002")
factory.protocol = ClientProtocol
reactor.connectTCP("www.csuiteexperiment.com", 9002, factory)
reactor.run()
