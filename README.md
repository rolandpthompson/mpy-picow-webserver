* Overview

Using a Raspberry Pi Pico W, we create a local webserver connected to a Wifi network. Configuration files determin what pins to what - I built it based on a Waveshare Pico Relay B board (https://www.waveshare.com/wiki/Pico-Relay-B).
You can obviously change the Pin needs to your requirements. The board has 8 relays, and so that is as far as the lists go, again, can be changed if needed

* Future Dev

I'd like going forward to secure the calls, probably with basic auth. While it will be available only on a local network, I think it's a wise thing to sort.
May also change it to more of an API, and use POST instead of GET - then have a dedicated app/site instead of getting it to serve too much - its only a small at the end of the day.


* Getting Started

Be sure to create a folder on the Pico called **webroot**, then place the index.htm and style.css into it.
Copy all the other py files onto the / of the pico.

Use the pinnames.py to define the 'Button' names, leave what you don't need as an empty text, this will stop the buttons and logic being rendered for those Pins.

Network IP settings can be setup in the netconfig.py file.

Finally, create a file called **secrets.py**, this needs to store in the / of the Pico too. (this file for obvious reasons is ommitted from the Git repo)
This file should contain your Wifi details, file should be like:

secrets = {
        "ssid": "your wifi ssid",
        "pwd": "your wifi password
    }
    
* API Endpoints

Require base authentication

[POST]
/api/toggle/[RELAY1..RELAY8]

[POST]
/api/enable/[RELAY1..RELAY8]

[POST]
/api/disable/[RELAY1..RELAY8]

[GET]
/api/status
[Returns a Json Object with the status of the available relays]

[POST] - Include Payload as sample below
/api/status

[
  {
    "Relay": 1,
    "Name": "Pump",
    "State": 0
  },
  {
    "Relay": 2,
    "Name": "UV Light",
    "State": 0
  },
  {
    "Relay": 3,
    "Name": "Skimmer",
    "State": 0
  }
]