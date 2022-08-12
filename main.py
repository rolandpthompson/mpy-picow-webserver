import network
import socket
import time

from machine import Pin
import uasyncio as asyncio
from secrets import secrets
from netconfig import netconfig
from pinnames import pinnames

# relay pins
relay_pins = list((Pin(21, Pin.OUT, value=0), Pin(20, Pin.OUT, value=0), Pin(19, Pin.OUT, value=0), Pin(18, Pin.OUT, value=0), Pin(17, Pin.OUT, value=0), Pin(16, Pin.OUT, value=0), Pin(15, Pin.OUT, value=0), Pin(14, Pin.OUT, value=0)))

# initial relay states array storage
relay_state = list((0,0,0,0,0,0,0,0))

# default relay names - to be populated when started
relay_names = list(("", "", "", "", "", "", "", ""))

# heartbeat indicator
onboard = Pin("LED", Pin.OUT, value=0)

ssid = secrets["ssid"] 
password = secrets["pwd"] 
wlan = network.WLAN(network.STA_IF)

def connect_to_network():
    wlan.active(True)
    
    # use dhcp or a static address
    if netconfig["dhcp"] == False:
        wlan.ifconfig((netconfig["ip"], netconfig["subnet"], netconfig["gateway"], netconfig["dns"]))
        
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
    
    global relay_names
    
    buttonTemplate = "<a href='/RELAY'><button class='button buttonSTATE'>Turn NAME STATE</button></a>"
    html = ""
            
    for i in range(len(relay_names)):
        if relay_names[i-1] != "":
            tempButton = buttonTemplate.replace("RELAY", "R" + str(i))
            tempButton = tempButton.replace("NAME", relay_names[i-1])
            if relay_state[i-1] == 1:
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
    relay_commands = list((request.find("/R1"), request.find("/R2"), request.find("/R3"), request.find("/R4"), request.find("/R5"), request.find("/R6"), request.find("/R7"), request.find("/R8")))
    css = request.find('.css')
    
    global relay_state, relay_pins, relay_names

    # loop though our command and work on the relay
    for i in range(len(relay_names)):
        if relay_commands[i-1] == 6:
            relay_state[i-1] = invert_state(relay_state[i-1])
            relay_pins[i-1].value(relay_state[i-1])
      
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

    # setup active relays
    global relay_names
    if pinnames["1"] != "":
        relay_names[0] = pinnames["1"]
        
    if pinnames["2"] != "":
        relay_names[1] = pinnames["2"]

    if pinnames["3"] != "":
        relay_names[2] = pinnames["3"]

    if pinnames["4"] != "":
        relay_names[3] = pinnames["4"]

    if pinnames["5"] != "":
        relay_names[4] = pinnames["5"]
        
    if pinnames["6"] != "":
        relay_names[5] = pinnames["6"]

    if pinnames["7"] != "":
        relay_names[6] = pinnames["7"]

    if pinnames["8"] != "":
        relay_names[7] = pinnames["8"]


    print('Connecting to Network...')
    connect_to_network()
    
    print('Setting up webserver...')
    asyncio.create_task(asyncio.start_server(serve_client, "0.0.0.0", 80))
    while True:
        onboard.on()
        print("heartbeat")
        await asyncio.sleep(0.25)
        onboard.off()
        await asyncio.sleep(5)
        
try:
    asyncio.run(main())
finally:
    syncio.new_event_loop()