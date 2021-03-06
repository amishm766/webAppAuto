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
import sqlite3
import subprocess
import RPi.GPIO as GPIO

from datetime import datetime
from picamera import PiCamera
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as figureCanvas
from flask import Flask, render_template, send_file, make_response, request


# Setting "utf8" as default encoding

reload(sys)
sys.setdefaultencoding('utf8')


home = Flask(__name__)

con = sqlite3.connect('../sensorsData.db', check_same_thread = False)
curs = con.cursor()

led = [26,12,16,20]
ledSts = ['0','0','0','0']

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for pin in led:
    GPIO.setup(pin, GPIO.OUT)


ledSts = ['0','0','0','0']

# the main route
@home.route("/")
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

# Gets the IP Address
def getaddr(ifname):

    """ Defines 'getaddr' as well as ifname arguement later  """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24]) 


if __name__ == "__main__":

    try:
        ip = getaddr('wlan0')
        home.run(host=ip, port=8080, debug=True)
        
    finally:
        GPIO.cleanup()


