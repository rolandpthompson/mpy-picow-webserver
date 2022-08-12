import network
import socket
import time

from machine import Pin
import uasyncio as asyncio
from secrets import secrets
from pinnames import pinnames

# Define pins for our relay
RELAY_1 = Pin(21, Pin.OUT, value=0)
RELAY_2 = Pin(20, Pin.OUT, value=0)
RELAY_3 = Pin(19, Pin.OUT, value=0)
RELAY_4 = Pin(18, Pin.OUT, value=0)
RELAY_5 = Pin(17, Pin.OUT, value=0)
RELAY_6 = Pin(16, Pin.OUT, value=0)
RELAY_7 = Pin(15, Pin.OUT, value=0)
RELAY_8 = Pin(14, Pin.OUT, value=0)

relay_1_state = 0
relay_2_state = 0
relay_3_state = 0
relay_4_state = 0
relay_5_state = 0
relay_6_state = 0
relay_7_state = 0
relay_8_state = 0

onboard = Pin("LED", Pin.OUT, value=0)

ssid = secrets["ssid"] 
password = secrets["pwd"] 
wlan = network.WLAN(network.STA_IF)

def connect_to_network():
    wlan.active(True)
    wlan.config(pm = 0xa11140) # Disable power-save mode
    wlan.connect(ssid, password)
    
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1

        print('waiting for connection...')
        time.sleep(1)
    
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()

        print('ip = ' + status[0])
        
def build_button_controls(response):
    
    global relay_1_state
    
    buttonTemplate = "<a href='/RELAY'><button class='button buttonSTATE'>Turn NAME STATE</button></a>"
    html = ""
    if pinnames["1"] != "":
        tempButton = buttonTemplate.replace("RELAY", "R1")
        tempButton = tempButton.replace("NAME", pinnames["1"])
        if relay_1_state == 1:
            html = html + tempButton.replace("STATE", "Off")
        else:
            html = html + tempButton.replace("STATE", "On")
    
    # inject the html buttons
    return response.replace("CMDS", html) 

def invert_state(currentstate):
    if currentstate == 0:
        return 1
    else:
        return 0

async def serve_client(reader, writer):
    print("Client connected")
    request_line = await reader.readline()
    print("Request:", request_line)
    
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass   
    
    # our request
    request = str(request_line)
    
    # items to look our for on our request
    RELAY_1_COMMAND = request.find('/R1')
    
    
    
    RELAY_1_ON_COMMAND = request.find('/R1ON')
    RELAY_1_OFF_COMMAND = request.find('/R1OFF')
    RELAY_2_ON_COMMAND = request.find('/R2ON')
    RELAY_2_OFF_COMMAND = request.find('/R2OFF')
    RELAY_3_ON_COMMAND = request.find('/R3ON')
    RELAY_3_OFF_COMMAND = request.find('/R3OFF')
    RELAY_4_ON_COMMAND = request.find('/R4ON')
    RELAY_4_OFF_COMMAND = request.find('/R4OFF')
    RELAY_5_ON_COMMAND = request.find('/R5ON')
    RELAY_5_OFF_COMMAND = request.find('/R5OFF')
    RELAY_6_ON_COMMAND = request.find('/R6ON')
    RELAY_6_OFF_COMMAND = request.find('/R6OFF')
    RELAY_7_ON_COMMAND = request.find('/R7ON')
    RELAY_7_OFF_COMMAND = request.find('/R7OFF')
    RELAY_8_ON_COMMAND = request.find('/R8ON')
    RELAY_8_OFF_COMMAND = request.find('/R8OFF')
    css = request.find('.css')
    
    global relay_1_state
    
    if RELAY_1_COMMAND == 6:
        relay_1_state = invert_state(relay_1_state)
        RELAY_1.value(relay_1_state)
    
    if RELAY_1_ON_COMMAND == 6:
        relay_1_state = 1
        RELAY_1.value(relay_1_state)

    if RELAY_1_OFF_COMMAND == 6:
        RELAY_1.value(0)

    if RELAY_2_ON_COMMAND == 6:
        RELAY_2.value(1)

    if RELAY_2_OFF_COMMAND == 6:
        RELAY_2.value(0)

    if RELAY_3_ON_COMMAND == 6:
        RELAY_3.value(1)

    if RELAY_3_OFF_COMMAND == 6:
        RELAY_3.value(0)

    if RELAY_4_ON_COMMAND == 6:
        RELAY_4.value(1)

    if RELAY_4_OFF_COMMAND == 6:
        RELAY_4.value(0)

    if RELAY_5_ON_COMMAND == 6:
        RELAY_5.value(1)

    if RELAY_5_OFF_COMMAND == 6:
        RELAY_5.value(0)

    if RELAY_6_ON_COMMAND == 6:
        RELAY_6.value(1)

    if RELAY_6_OFF_COMMAND == 6:
        RELAY_6.value(0)

    if RELAY_7_ON_COMMAND == 6:
        RELAY_7.value(1)
        
    if RELAY_7_OFF_COMMAND == 6:
        RELAY_7.value(0)
    
    if RELAY_8_ON_COMMAND == 6:
        RELAY_8.value(1)

    if RELAY_8_OFF_COMMAND == 6:
        RELAY_8.value(0)
   
    # handle if a CSS request
    if css > 0:
        # 'GET /webroot/style.css HTTP/1.1\r\n'
        print("CSS Requested")
        
        requestedfile = request[6:css+4]
        f = open(requestedfile)
        response = f.read()
        f.close()
        
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/css\r\n\r\n')
    else: # else standard html
        
        requestedfile = "webroot/index.htm"
        f = open(requestedfile)
        response = f.read()
        f.close()
        # need to add our button commands here.
        response = build_button_controls(response)
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')

    writer.write(response)
    
    await writer.drain()
    await writer.wait_closed()
    print("Client disconnected")
    
async def main():
    global relay_1_state
    
    print('Connecting to Network...')
    connect_to_network()
    
    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))
    while True:
        onboard.on()
        print("heartbeat")
        if relay_1_state == 0:
            print("off")
        else:
            print("on")
        await asyncio.sleep(0.25)
        onboard.off()
        await asyncio.sleep(5)
        
try:
    asyncio.run(main())
finally:
    syncio.new_event_loop()