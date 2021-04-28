import socket, json, requests
import datetime
from lxml import etree
import time
import what3words

# 	ATAK 'Geo Bot' for geo conversions
# 	Tested with https://github.com/tkuester/taky
#
#	Copyright (c) 2021 Farrant Consulting Ltd
#
#	Permission is hereby granted, free of charge, to any person obtaining a copy
#	of this software and associated documentation files (the "Software"), to deal
#	in the Software without restriction, including without limitation the rights
#	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#	copies of the Software, and to permit persons to whom the Software is
#	furnished to do so, subject to the following conditions:
#
#	The above copyright notice and this permission notice shall be included in all
#	copies or substantial portions of the Software.
#
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#	SOFTWARE.


# *** CHANGE ME ***

# ADVANCED
TAK_SERVER_ADDRESS = "127.0.0.1"  # The TAK server's hostname or IP address
TAK_SERVER_PORT = 8087        # The TCP CoT port used by the server for XML
W3W_API_KEY = ""	# YOUR API KEY

geocoder = what3words.Geocoder(W3W_API_KEY)

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
	</detail></event>'
	return msg.encode("utf-8")

def register():
	ts=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
	tots=(datetime.datetime.now()+datetime.timedelta(days=90)).strftime('%Y-%m-%dT%H:%M:%SZ')
	print("Registering")
	msg='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\
	<event version="2.0" uid="GEO-BOT" type="a-f-G-U-C" time="'+ts+'" start="'+ts+'" stale="'+tots+'" how="h-e">\
	<point lat="0" lon="0" hae="0" ce="9999999" le="9999999"/>\
	<detail><takv os="0" version="0" device="A Python script :P" platform="Python"/>\
	<contact callsign="GEO BOT" endpoint="*:-1:stcp"/><uid Droid="GEO BOT"/>\
	<precisionlocation altsrc="" geopointsrc="USER"/><__group role="Team Member" name="Cyan"/>\
	<status battery="100"/><track course="0.0" speed="0.0"/></detail></event>'
	return msg.encode("utf-8")


def respond(s,xml):
	ts=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
	request=parseCoT(xml)
	print(ts,request)
	s.sendall(geochat("ZUJ..",request["atakuid"]))
	res = geocoder.convert_to_3wa(what3words.Coordinates(request["lat"], request["lon"]))
	print(res)
	#{'country': 'ES', 'square': {'southwest': {'lng': 2.713511, 'lat': 39.574844}, 'northeast': {'lng': 2.713546, 'lat': 39.574871}}, 'nearestPlace': "Coll d'en Rabassa, Balearic Islands", 'coordinates': {'lng': 2.713529, 'lat': 39.574857}, 'words': 'linen.scraper.arching', 'language': 'en', 'map': 'https://w3w.co/linen.scraper.arching'}
	s.sendall(geochat(res["words"],request["atakuid"]))

def ping(s):
	uuid=time.time()
	ts=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
	tots=(datetime.datetime.now()+datetime.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
	msg='<event version="2.0" uid="RF-BOT-ping" type="t-x-c-t"\
	time="'+ts+'" start="'+ts+'" stale="'+tots+'" how="m-g">\
	<point lat="0.0" lon="0.0" hae="0.0" ce="9999999" le="9999999"/>\
	<detail/></event>'
	s.sendall(msg.encode("utf-8"))

# Connect to a TAK server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.connect((TAK_SERVER_ADDRESS, TAK_SERVER_PORT))
	start = time.time()

	# Announce to all we're ready for tasking
	s.sendall(register())
	s.sendall(geochat('GEO-BOT online','All Chat Rooms'))

	while True:
		elapsed = time.time() - start
		if elapsed > 8:
			ping(s) # keep-alive
			start = time.time()

		try:
			xml = s.recv(1024).decode("utf-8")
			if "Chat" in xml:
				respond(s,xml)
		except:
			print(xml)
			pass
