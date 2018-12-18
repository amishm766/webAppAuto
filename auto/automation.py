
#!/usr/bin/env python

# ----encoding:- utf-8 ----
# created by Ankit Mishra
# 28 july,2018

"""
    Raspberry pi based web controlled home automation from anywhere in the world(remotely)
"""

# Including some python libraries

import os
import io
import sys
import math
import time
import fcntl
import struct
import socket
import select
import subprocess
import numpy as np
import pandas as pd
import RPi.GPIO as GPIO
from datetime import datetime
from picamera import PiCamera
from flask_api import FlaskAPI
from flask import Flask, request, render_template, send_file, make_response, request, redirect


# Setting "utf8" as default encoding

#reload(sys)
#sys.setdefaultencoding('utf8')
global check, users
check = False

home = FlaskAPI(__name__)


led = (26,12,16,20)
ledSts = ['0','0','0','0']

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in led:
    GPIO.setup(pin, GPIO.OUT)
    

ledSts = ['0','0','0','0']

# Route for handling the login page logic
@home.route('/', methods=['GET', 'POST'])
def login():
    global check
    check = True
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            check = True
            addr = request.remote_addr
            print(addr)
            return redirect(('/login'))
    return render_template('login.html', error = error)


# the main route
@home.route("/login")
def index():
    
    """ Reading status of the appliances whether ON or OFF """
    for pin in range (len(led)):
        ledSts[pin] = GPIO.input(led[pin])
        

    """ return the data to the html page(index.html) """
    data = {
            'title': 'STATUS OF APPLIANCES',
            'led0' : ledSts[0],
            'led1' : ledSts[1],
            'led2' : ledSts[2],
            'led3' : ledSts[3]
            }

    return render_template("index.html", **data)
    
@home.route("/<appliance>/<action>")
def action(appliance, action):
    
    if check:
        """ check for which appliance the request is created from webpage """
        if appliance == 'led0':
            actuator = led[0]
        if appliance == 'led1':
            actuator = led[1]
        if appliance == 'led2':
            actuator = led[2]
        if appliance == 'led3':
            actuator = led[3]
        
        """ take action on the appliances as per the request"""
        GPIO.output(actuator, GPIO.HIGH) if action == 'ON' else GPIO.output(actuator, GPIO.LOW)

        """ Reading status of the appliances whether ON or OFF """
        for pin in range(len(led)):
            ledSts[pin] = GPIO.input(led[pin])
        
        """ the values or data that has to be returned to webpage """
        data = {
                'led0' : ledSts[0],
                'led1' : ledSts[1],
                'led2' : ledSts[2],
                'led3' : ledSts[3]
                }

        """ return the data to the html page(index.html) """
        return render_template("index.html", **data)
	
    else:
        return redirect(('/'))
        
# Gets the IP Address
def getaddr(ifname):
    global s
    """ Defines 'getaddr' as well as ifname arguement later  """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24]) 


if __name__ == "__main__":

    try:
        ip = getaddr('eth0')
        home.run(host='0.0.0.0', port=80, debug=True)
        
    finally:
        GPIO.cleanup()


