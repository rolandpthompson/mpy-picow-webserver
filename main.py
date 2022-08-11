import network
import socket
import time

from machine import Pin
import uasyncio as asyncio

# led = Pin(15, Pin.OUT)
onboard = Pin("LED", Pin.OUT)

onboard_status = Pin.low

ssid = 'Rolands iPhone'
password = 'R79ds82h'

# html = """
#     <!DOCTYPE html><html>
#     <head><meta name='viewport' content='width=device-width, initial-scale=1'>
#     <link rel='icon' href='data:,'>

#     <style>
#     .button {;
#     border: none;
#     color: white;
#     padding: 15px 32px;
#     text-align: center;
#     text-decoration: none;
#     display: inline-block;
#     font-size: 16px;
#     margin: 4px 2px;
#     cursor: pointer;
#     }
#     .buttonON {background-color: #4CAF50;} /* Green */
#     .buttonOFF {background-color: #a83232;} /* Red */
#     </style>
#     </head>
#     <body> <h1>Pico W</h1>
#         <p>%s</p>
# """

# if (onboard_status == Pin.low):
#     html += "<a href='/light/on'><button class='button buttonON'>Turn ON</button></a>"

# if (onboard_status == Pin.high):
#     html += "<a href='/light/off'><button class='button buttonOFF'>Turn OFF</button></a>"

# html += """
#     </body>
# </html>
# """

html = "<!DOCTYPE html><html>hello!</html>"

wlan = network.WLAN(network.STA_IF)


def connect_to_network():
    wlan.active(True)
    wlan.config(pm=0xa11140)  # Disable power-save mode
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
    led_on = request.find('/light/on')
    led_off = request.find('/light/off')
    print('led on = ' + str(led_on))
    print('led off = ' + str(led_off))

    stateis = ""
    if led_on == 6:
        print("led on")
        onboard_status = Pin.high
        onboard.value(onboard_status)
        stateis = "LED is ON"

    if led_off == 6:
        print("led off")
        onboard_status = Pin.low
        onboard.value(onboard_status)
        stateis = "LED is OFF"

    response = html % stateis
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
        #onboard.on()
        print("heartbeat")
        await asyncio.sleep(0.25)
        #onboard.off()
        await asyncio.sleep(5)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
