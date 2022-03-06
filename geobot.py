import socket, json, requests
import datetime
from lxml import etree
import time
import what3words
import sys
from OSGridConverter import latlong2grid


# 	ATAK 'Geo Bot' for geo conversions
# 	Works with https://github.com/tkuester/taky
#
# 	THIS IS PUBLIC DOMAIN CODE. GO NUTS.
#	support@cloudrf.com


# *** CHANGE ME ***

# ADVANCED
TAK_SERVER_ADDRESS = "127.0.0.1"  # The TAK server's hostname or IP address
TAK_SERVER_PORT = 8087        # The TCP CoT port used by the server for XML
W3W_API_KEY = ""	# YOUR API KEY
debug = 0
geocoder = what3words.Geocoder(W3W_API_KEY)

# DEBUG SWITCH
if len(sys.argv) > 1:
	if sys.argv[1] == "-d":
		debug=1

# w3w = What 3 words API
# os = WGS84 to OSGB conversion

# ADD YOUR AWESOME GEO CONVERSION HERE:
commands = ["w3w","bng","ddd"]
helpers = ["WGS84 to What-3-words","WGS84 to OSGB (BNG)","Decimal degree dropper"]

def markerCoT(type,dest,lat,lon):
	uuid=time.time()
	ts=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
	tots=(datetime.datetime.now()+datetime.timedelta(days=90)).strftime('%Y-%m-%dT%H:%M:%SZ')
	print("Dropping marker")
	msg='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
	msg+='<event version="2.0" uid="GEO-BOT.'+str(uuid)+'" type="'+type+'" time="'+ts+'" start="'+ts+'" stale="'+tots+'" how="h-g-i-g-o">'
	msg+='<point lat="'+str(lat)+'" lon="'+str(lon)+'" hae="9999999.0" ce="9999999.0" le="9999999.0"/>'
	msg+='<detail><status readiness="true"/><archive/><remarks/>'
	msg+='<contact callsign="?"/><precisionlocation altsrc="DTED0"/><usericon iconsetpath="COT_MAPPING_2525C/a-u/'+type+'"/>'
	msg+='<link uid="GEO-BOT" production_time="'+ts+'" type="'+type+'" parent_callsign="GEO-BOT" relation="p-p"/><color argb="-1"/></detail></event>'
	if debug:
		print("TX",msg)
	return msg.encode("utf-8")

def parseCoT(xml):
	root = etree.fromstring(xml.encode("utf-8"))
	lat=round(float(root.xpath("//event/point")[0].attrib["lat"]),5)
	lon=round(float(root.xpath("//event/point")[0].attrib["lon"]),5)
	try:
		cs=root.xpath("//event/detail/__chat")[0].attrib["senderCallsign"]
		msg=root.xpath("//event/detail/remarks/text()")[0]
		uid=root.xpath("//event/detail/link")[0].attrib["uid"]
		return {"atakuid": uid, "atakcs": cs, "lat": lat, "lon": lon, "cmd": msg}
	except:
		return xml

def geochat(msg,dest):
	uuid=time.time()
	ts=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
	msg = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
	<event version="2.0" uid="GeoChat.GEO-BOT.'+dest+'.'+str(uuid)+'"\
	 type="b-t-f" time="'+ts+'" start="'+ts+'" stale="'+ts+'" how="h-g-i-g-o">\
	<point lat="0.0" lon="0.0" hae="9999999.0" ce="9999999.0" le="9999999.0"/>\
	<detail>\
	<__chat parent="RootContactGroup" groupOwner="false" chatroom="'+dest+'" id="'+dest+'" senderCallsign="GEO BOT">\
	<chatgrp uid0="GEO-BOT" uid1="'+dest+'" id="'+dest+'"/></__chat><link uid="GEO-BOT" type="a-f-G-U-C" relation="p-p"/>\
	<remarks source="BAO.F.ATAK.GEO-BOT" to="'+dest+'" time="'+ts+'">'+msg+'</remarks>\
	<__serverdestination destinations="'+TAK_SERVER_ADDRESS+':4242:tcp:GEO-BOT"/></detail></event>'
	if debug:
		print("TX",msg)
	return msg.encode("utf-8")

def register():
	ts=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
	tots=(datetime.datetime.now()+datetime.timedelta(days=90)).strftime('%Y-%m-%dT%H:%M:%SZ')
	print("Registering")
	msg='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
	<event version="2.0" uid="GEO-BOT" type="a-f-G-U-C" time="'+ts+'" start="'+ts+'" stale="'+tots+'" how="h-e">\
	<point lat="0" lon="0" hae="9999999.0" ce="9999999.0" le="9999999.0"/>\
	<detail><takv os="0" version="0" device="A Python script :P" platform="Python"/>\
        <contact xmppUsername="test" endpoint="*:-1:stcp" callsign="GEO BOT"/>\
	<contact callsign="GEO BOT" endpoint="*:-1:stcp"/><uid Droid="GEO BOT"/>\
	<precisionlocation altsrc="" geopointsrc="USER"/><__group role="Team Member" name="Cyan"/>\
	<status battery="100"/><track course="0.0" speed="0.0"/></detail></event>'
	if debug:
		print("TX",msg)
	return msg.encode("utf-8")


def respond(s,xml):
	ts=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
	request=parseCoT(xml)
	print(ts,request)
	cmd = request["cmd"][:3].strip()
	if cmd in commands:
		print(request["lat"],request["lon"])
		if (abs(request["lat"])+abs(request["lon"])) < 1.0:
			s.sendall(geochat("Set your location (%.1f,%.1f )before requesting a conversion!" % (request["lat"],request["lon"]),request["atakuid"]))
			return

		# WHAT 3 WORDS
		if cmd == "w3w":
			s.sendall(geochat("Tranforming location %.5f, %.5f..." % (request["lat"],request["lon"]),request["atakuid"]))
			res = geocoder.convert_to_3wa(what3words.Coordinates(request["lat"], request["lon"]))
			if "words" in res:
				s.sendall(geochat(res["words"],request["atakuid"]))
			else:
				print(res)
				s.sendall(geochat(res["error"]["message"],request["atakuid"]))

		# OSGB / EPSG
		if cmd == "bng":
			s.sendall(geochat("Tranforming location %.5f, %.5f..." % (request["lat"],request["lon"]),request["atakuid"]))
			bng=latlong2grid(request["lat"], request["lon"])
			print(bng)
			s.sendall(geochat(str(bng),request["atakuid"]))

		if cmd == "ddd":
			print(request,cmd)
			ack = "Bad location"
			# RULES
			loc = request["cmd"][3:].strip()

			if len(loc) < 10:
				ack = "Coordinates should be longer than 10 chars"
			if len(loc) > 32:
				ack = "Coordinates should be shorter than 32 chars"
			delim = "?"
			# Split it
			if "," in loc:
				delim = ","
			elif " " in loc:
				delim = " "
			else:
				ack = "Coordinates delimiter should be a , or a space"

			if delim != "?":
				parts = loc.split(delim)
				try:
					lat = float(parts[0])
					lon = float(parts[1])
					# sanity check coords
					if lat < -90 or lat > 90:
						error = "Latitude out of bounds: -90. to 90."
					
				except:
					s.sendall(geochat("Failed to parse coordinates",request["atakuid"]))
					return

				marker = markerCoT("a-u-G",request["atakuid"],lat,lon)
				s.sendall(marker)
				s.sendall(geochat("Dropped marker at "+str(lat)+","+str(lon),request["atakuid"]))
			else:
				s.sendall(geochat(str(ack),request["atakuid"]))
	else:
		s.sendall(geochat("Available services. Ensure you have set your lat/lon either manually or with a GPS",request["atakuid"]))
		c = 0
		while c < len(commands):
			s.sendall(geochat(commands[c]+": "+helpers[c],request["atakuid"]))
			c+=1



def ping(s):
	uuid=time.time()
	ts=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
	tots=(datetime.datetime.now()+datetime.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
	msg='<event version="2.0" uid="RF-BOT-ping" type="t-x-c-t"\
	time="'+ts+'" start="'+ts+'" stale="'+tots+'" how="m-g">\
	<point lat="0.0" lon="0.0" hae="0.0" ce="9999999" le="9999999"/>\
	<detail/></event>'
	if debug:
		print("TX",msg)
	s.sendall(msg.encode("utf-8"))

# Connect to a TAK server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((TAK_SERVER_ADDRESS, TAK_SERVER_PORT))
	start = time.time()

	if debug:
		print("Connected to server %s:%s" % (TAK_SERVER_ADDRESS, TAK_SERVER_PORT))

	# Announce to all we're ready for tasking
	s.sendall(register())
	s.sendall(geochat('GEO-BOT online','All Chat Rooms'))

	while True:

		try:
			xml = s.recv(1024).decode("utf-8")
			if "Chat" in xml:
				respond(s,xml)
			else:
				if debug and len(xml) > 1:
					print("RX",xml)
				pass
		except:
			print("Received bad XML data from server")
			print(xml)
