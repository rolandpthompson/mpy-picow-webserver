import network
import socket
import time
import json

from machine import Pin
import uasyncio as asyncio

from secrets import secrets
from netconfig import netconfig
from pinnames import pinnames

# relay pins [RELAY1 .. RELAY8]
relay_pins = list((Pin(21, Pin.OUT, value=0), Pin(20, Pin.OUT, value=0), Pin(19, Pin.OUT, value=0), Pin(18, Pin.OUT, value=0), Pin(17, Pin.OUT, value=0), Pin(16, Pin.OUT, value=0), Pin(15, Pin.OUT, value=0), Pin(14, Pin.OUT, value=0)))

# initial relay states array storage  [RELAY1 .. RELAY8]
relay_state = list((0,0,0,0,0,0,0,0))

# default relay names - to be populated when started  [RELAY1 .. RELAY8]
relay_names = list(("", "", "", "", "", "", "", ""))

# relay commands
relay_commands = list((0,0,0,0,0,0,0,0))

# heartbeat indicator
onboard = Pin("LED", Pin.OUT, value=0)

ssid = secrets["ssid"] 
password = secrets["pwd"] 
wlan = network.WLAN(network.STA_IF)
base64Encoded = netconfig["baseEncoding"]
response = ""
payload = ""

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
    
    #buttonTemplate = "<a href='/RELAY'><button class='button buttonSTATE'>Turn NAME STATE</button></a>"
    buttonTemplate = """<form action="" method="post">
                            <input type="submit" name="RELAY" value="Turn NAME STATE" class="button buttonSTATE" />
                        </form>"""
        
    html = ""
            
    for i in range(len(relay_names)):
        if relay_names[i-1] != "":
            tempButton = buttonTemplate.replace("RELAY", "RELAY" + str(i))
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
    
def check_authorised(request, writer):
    global base64Encoded
    if request.find(base64Encoded) > 0:
        return True
    else:
        # not authorised...
        writer.write('HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm="Secure"\r\nContent-Type: text/html\r\n\r\n') # Bad Request
        return False
    
def handle_get(request, writer):

    global relay_state, relay_pins, relay_names, response         
    css = request.find('.css')
    
    # getting status (api)
    if request.find("/api/status") > 0:
        if check_authorised(request, writer):
            # get our state as object and add to the response
            pinstate_asobject()
          
            writer.write('HTTP/1.1 200 OK\r\nContent-type: application/json\r\n\r\n') # OK
    
    # handle if a CSS request
    elif css > 0:
        requestedfile = request[6:css+4]
        f = open(requestedfile)
        response = f.read()
        f.close()
        
        writer.write('HTTP/1.1 200 OK\r\nContent-type: text/css\r\n\r\n')
    else: # else standard html
        requestedfile = "webroot/index.htm" # TODO: Maybe read this file once at startup and store so we dont need to read everytime..
        f = open(requestedfile)
        response = f.read()
        f.close()
        
        # need to add our button commands here.
        response = build_button_controls(response)
        writer.write('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
        
def handle_post(request, reader, writer):
    
    global relay_state, relay_pins, relay_names, response
    
    # authorised?
    if check_authorised(request, writer):
        # what are we doing
        if request.find("/api/status") > 0: # setting the status using json, then return the pin states

            # TODO
            
            # get our state as object and add to the response
            pinstate_asobject()
           
            writer.write('HTTP/1.1 200 OK\r\nContent-type: application/json\r\n\r\n') # OK

        elif request.find("/api/toggle") > 0:
            # loop though our command and toggle relay
            for i in range(len(relay_names)):
                if relay_commands[i-1] == 19:
                    relay_state[i-1] = invert_state(relay_state[i-1])
                    relay_pins[i-1].value(relay_state[i-1])
                    break
            
            writer.write('HTTP/1.1 204 No Content\r\n\r\n') # no content response - OK
            
        elif request.find("/api/enable") > 0:
            # loop though our command and enable relay
            for i in range(len(relay_names)):
                if relay_commands[i-1] == 19:
                    relay_state[i-1] = 1
                    relay_pins[i-1].value(relay_state[i-1])
                    break
                    
            writer.write('HTTP/1.1 204 No Content\r\n\r\n') # no content response - OK                    
                    
        elif request.find("/api/disable") > 0:
            # loop though our command and disable relay
            for i in range(len(relay_names)):
                if relay_commands[i-1] == 20:
                    relay_state[i-1] = 0
                    relay_pins[i-1].value(relay_state[i-1])
                    break

            writer.write('HTTP/1.1 204 No Content\r\n\r\n') # no content response - OK

        else:
            writer.write('HTTP/1.1 400 Bad Request\r\n\r\n') # Bad Request

    
def pinstate_asobject():
    global relay_state, relay_names, response
    
    # finally, get and return the state of the pins as json
    data = []
    # loop though our relays to get the state
    for i in range(len(relay_names)):
        if relay_names[i-1] != "":
            data.append({'Relay': i, 'Name': relay_names[i-1],'State': relay_state[i-1]})
    
    response = json.dumps(data)

async def serve_client(reader, writer):
    
    global response, relay_commands, payload
    
    #s = await reader.read(2048)
    #print(s)
    #message = json.loads(s.decode())
    #print(message)
    
    print("Client connected")
    line = await reader.read(2048)

    request = str(line)
    print(str(request))
    
    # try and get any content..
    closePos = request.find("Connection: close") + len('Connection: close') + 8
    payload = request[closePos:]
    
    # items to look our for on our request
    relay_commands = list((request.find("RELAY1"), request.find("RELAY2"), request.find("RELAY3"), request.find("RELAY4"), request.find("RELAY5"), request.find("RELAY6"), request.find("RELAY7"), request.find("RELAY8")))
    
    # what type of action are we doing
    isget = request.find("GET ") > 0;
    ispost = request.find("POST ") > 0;

    global response

    # clear response
    response = ""
    if isget:
        handle_get(request, writer)
    elif ispost:
        handle_post(request, reader, writer)
    else:
        writer.write('HTTP/1.1 400 Bad Request\r\n\r\n') # Bad Request

    if response != "":
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
        # print("heartbeat")
        await asyncio.sleep(0.25)
        onboard.off()
        await asyncio.sleep(5)
        
try:
    asyncio.run(main())
finally:
    syncio.new_event_loop()