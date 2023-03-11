import os
import time
import json
import board
import wifi
import socketpool
import digitalio
from adafruit_httpserver.mime_type import MIMEType
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.server import HTTPServer


# Configure built-in LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = False

#  Configure WiFi
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool) # type: ignore

@server.route("/")
def base(request: HTTPRequest):
    led.value = True
    response_data = {"status": "OK"}
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