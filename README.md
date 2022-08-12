Be sure to create a folder on the Pico called #webroot#, then place the index.htm and style.css into it.
Copy all the other py files onto the / of the pico.

Use the pinnames.py to define the 'Button' names, leave what you don't need as an empty text, this will stop the buttons and logic being rendered for those Pins.

Network IP settings can be setup in the netconfig.py file.

Finally, create a file called #secrets.py#, this needs to store in the / of the Pico too. (this file for obvious reasons is ommitted from the Git repo)
This file should contain your Wifi details, file should be like:

secrets = {
        "ssid": "your wifi ssid",
        "pwd": "your wifi password
    }