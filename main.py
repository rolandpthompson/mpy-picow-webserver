import network
import socket
import time

from machine import Pin
import uasyncio as asyncio


RELAY_1 = Pin(21, Pin.OUT)
RELAY_2 = Pin(20, Pin.OUT)
RELAY_3 = Pin(19, Pin.OUT)
RELAY_4 = Pin(18, Pin.OUT)
RELAY_5 = Pin(17, Pin.OUT)
RELAY_6 = Pin(16, Pin.OUT)
RELAY_7 = Pin(15, Pin.OUT)
RELAY_8 = Pin(14, Pin.OUT)

onboard = Pin("LED", Pin.OUT, value=0)

ssid = "thethompsons-iot"
password = "T11hr19d_"

html = """<!DOCTYPE html>
<html>
    <head>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Pico W</title>
    <link rel="stylesheet" href="/webroot/style.css">
    </head>
    <body> <h1>Pico W</h1>
       <a href='/R1ON'><button class='button buttonON'>Turn Relay 1 ON</button></a>
       <a href='/R1OFF'><button class='button buttonOFF'>Turn Relay 1 OFF</button></a>
       <a href='/R2ON'><button class='button buttonON'>Turn Relay 2 ON</button></a>
       <a href='/R2OFF'><button class='button buttonOFF'>Turn Relay 2 OFF</button></a>
       <a href='/R3ON'><button class='button buttonON'>Turn Relay 3 ON</button></a>
       <a href='/R3OFF'><button class='button buttonOFF'>Turn Relay 3 OFF</button></a>
       <a href='/R4ON'><button class='button buttonON'>Turn Relay 4 ON</button></a>
       <a href='/R4OFF'><button class='button buttonOFF'>Turn Relay 4 OFF</button></a>
       <a href='/R5ON'><button class='button buttonON'>Turn Relay 5 ON</button></a>
       <a href='/R5OFF'><button class='button buttonOFF'>Turn Relay 5 OFF</button></a>
       <a href='/R6ON'><button class='button buttonON'>Turn Relay 6 ON</button></a>
       <a href='/R6OFF'><button class='button buttonOFF'>Turn Relay 6 OFF</button></a>
       <a href='/R7ON'><button class='button buttonON'>Turn Relay 7 ON</button></a>
       <a href='/R7OFF'><button class='button buttonOFF'>Turn Relay 7 OFF</button></a>
       <a href='/R8ON'><button class='button buttonON'>Turn Relay 8 ON</button></a>
       <a href='/R8OFF'><button class='button buttonOFF'>Turn Relay 8 OFF</button></a>
       <p>%s</p>        
    </body>
</html>
"""

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


async def serve_client(reader, writer):
    print("Client connected")
    request_line = await reader.readline()
    print("Request:", request_line)
    
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass
    
    
    request = str(request_line)
    RELAY_1_ON = request.find('/R1ON')
    RELAY_1_OFF = request.find('/R1OFF')
    RELAY_2_ON = request.find('/R2ON')
    RELAY_2_OFF = request.find('/R2OFF')
    RELAY_3_ON = request.find('/R3ON')
    RELAY_3_OFF = request.find('/R3OFF')
    RELAY_4_ON = request.find('/R4ON')
    RELAY_4_OFF = request.find('/R4OFF')
    RELAY_5_ON = request.find('/R5ON')
    RELAY_5_OFF = request.find('/R5OFF')
    RELAY_6_ON = request.find('/R6ON')
    RELAY_6_OFF = request.find('/R6OFF')
    RELAY_7_ON = request.find('/R7ON')
    RELAY_7_OFF = request.find('/R7OFF')
    RELAY_8_ON = request.find('/R8ON')
    RELAY_8_OFF = request.find('/R8OFF')
    css = request.find('.css')
    
    stateis = ""
    if RELAY_1_ON == 6:
        RELAY_1.value(1)
        stateis = "1 is ON"

    if RELAY_1_OFF == 6:
        RELAY_1.value(0)
        stateis = "1 is OFF"

    if RELAY_2_ON == 6:
        RELAY_2.value(1)
        stateis = "2 is ON"

    if RELAY_2_OFF == 6:
        RELAY_2.value(0)
        stateis = "2 is OFF"

    if RELAY_3_ON == 6:
        RELAY_3.value(1)
        stateis = "3 is ON"

    if RELAY_3_OFF == 6:
        RELAY_3.value(0)
        stateis = "3 is OFF"

    if RELAY_4_ON == 6:
        RELAY_4.value(1)
        stateis = "4 is ON"

    if RELAY_4_OFF == 6:
        RELAY_4.value(0)
        stateis = "4 is OFF"

    if RELAY_5_ON == 6:
        RELAY_5.value(1)
        stateis = "5 is ON"

    if RELAY_5_OFF == 6:
        RELAY_5.value(0)
        stateis = "5 is OFF"

    if RELAY_6_ON == 6:
        RELAY_6.value(1)
        stateis = "6 is ON"

    if RELAY_6_OFF == 6:
        RELAY_6.value(0)
        stateis = "6 is OFF"

    if RELAY_7_ON == 6:
        RELAY_7.value(1)
        stateis = "7 is ON"
        
    if RELAY_7_OFF == 6:
        RELAY_7.value(0)
        stateis = "7 is OFF"
    
    if RELAY_8_ON == 6:
        RELAY_8.value(1)
        stateis = "8 is On"

    if RELAY_8_OFF == 6:
        RELAY_8.value(0)
        stateis = "8 is OFF"

    response = html % stateis
    
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
        writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    
    writer.write(response)
    
    await writer.drain()
    await writer.wait_closed()
    print("Client disconnected")
    
async def main():
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