import os
import sys
import time
import serial
import RPi.GPIO as GPIO 

sys.path.append('/home/pi/Documents/lcd')
from lcd import *

class write_serial_device:
    global port
    global rcv
    rcv = ""
    
    def __init__(self, serialDevice):

        self.serialDevice = serialDevice
        print("connecting to %s" %self.serialDevice)
        if self.serialDevice == "GSM":
            self.port = serial.Serial("/dev/ttyUSB0", baudrate = 9600, timeout = 20)
        elif self.serialDevice == "gps":
            self.port = serial.Serial("/dev/ttyUSB1", baudrate = 9600, timeout = 20)

    def write_port(self, command, readByte, sleepTime):

        self.port.write(command+"\r")
        rcv = self.port.read(readByte)
        print (rcv)
        time.sleep(sleepTime)
        #print ("working")

    def call(self, mobNum):
        
        self.write_port("ATD+91%s;" %mobNum ,20,15)

    def send_msg(self, mobNum, message):
        command = "AT+CGMS"+ mobNum
        self.write_port(command, 10, 1)
        self.write_port("message",10,2)

MATRIX = [
            ['1','2','3','A'],
            ['4','5','6','B'],
            ['7','8','9','C'],
            ['*','0','#','D']
         ]

ROW = [20,16,12,26]
COL = [19,13,6,5]
#PIN = ['0','0','0','0']
#PIN =[]
#PIN = set()
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in ROW,COL:
    GPIO.setup(pin, GPIO.IN, pull_up_down= GPIO.PUD_UP)
    
def keypad():
    for j in range(4):
        GPIO.setup(COL[j], GPIO.OUT)
        GPIO.output(COL[j], 0)
        ch=0
        for i in range(4):
            if GPIO.input(ROW[i])==0:
                ch=MATRIX[i][j]
         
                print "Key Pressed:",ch
                time.sleep(0.25)
                return ch
                while (GPIO.input(ROW[i]) == 0):
                    pass
        GPIO.output(COL[j],1)
main()
lcd_clear()
lcd_string("Enter pin to", LCD_LINE_3)
lcd_string("open the gate", LCD_LINE_4)

def lock():
    PIN = []
    while True:
    
        key = 0
        key = keypad()
    
        if key >0:
            if key == '#':
                pin =0
                pin= ''.join(PIN)
                if pin == "1234":
                
                    lcd_string("correct pin", LCD_LINE_1)
                    lcd_string("gate opened", LCD_LINE_2)
                    time.sleep(2)
                    lcd_clear()
                    lcd_string("Enter pin to", LCD_LINE_3)
                    lcd_string("open the gate", LCD_LINE_4)
                    PIN = []
                    #PIN = set()
                else:
                    lcd_string("wrong pin try again!", LCD_LINE_1)
                    time.sleep(2)
                    lcd_clear()
                    lcd_string("Enter pin to", LCD_LINE_3)
                    lcd_string("open the gate", LCD_LINE_4)
                    calling = write_serial_device("GSM")
                    calling.call("9713490290")
                    PIN = []
                    #PIN = set()
            else:
                #PIN.add(key)
                PIN+=key
                lcd_byte(ord(key),True)
                time.sleep(0.5)
                print PIN

lock()
