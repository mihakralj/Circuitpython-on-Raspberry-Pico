import os
import ssl
import json
import board
import wifi
import socketpool
import digitalio

# requires adafruit_httpserver folder in /lib
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer
import adafruit_requests as requests

# Configure built-in LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False

#  Configure WiFi
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

#  call growee backend and get json with core data
def getData():
    url = "https://www.mygrowee.com/webresources/"
    socket = socketpool.SocketPool(wifi.radio)
    https = requests.Session(socket, ssl.create_default_context())
    response = https.post(url+"welcome/login", json={"userName":os.getenv('GROWEE_USERNAME'), "userPass":os.getenv('GROWEE_PASSWORD')})
    cookies = "JSESSIONID="+response.headers["set-cookie"].split(';')[0].split('=')[1]+ "; session_id="+response.json()["session_id"]
    data = https.get(url+"dashboard/userDeviceDetails", headers={"Cookie": cookies}).json()
    del data["waterLiterLevel"]
    del data["isTargetPHOn"]
    del data["isTargetECOn"]
    del data["ec_pumps_connected"]
    del data["is_ph_module_connected"]
    del data["is_ec_module_connected"]
    del data["device_id"]
    data["water_tmp"] = str(float(data["water_tmp"])*9/5 + 32)
    data["air_tmp"] = str(float(data["air_tmp"])*9/5 + 32)
    # returned fields: PH, EC, humidity, water_tmp, air_tmp, lastUpdate
    return data

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool) # type: ignore

@server.route("/")
def base(request: HTTPRequest):
    led.value = True
    response_data = getData()
    with HTTPResponse(request, content_type=MIMEType.TYPE_JSON) as response:
        response.send(json.dumps(response_data))
    led.value = False

# Start the server.
server.start(str(wifi.radio.ipv4_address))
print(f"Listening on http://{wifi.radio.ipv4_address}:80")

while True:
    try:
        server.poll()
    except OSError as error:
        print(error)
        continue