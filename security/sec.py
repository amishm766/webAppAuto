#!/usr/bin/env python
# Author : Ankit Mishra
# Date: 30 july, 2018

""" home security system and theft protection using RASPBERRY PI """
# Including some packages
import os
import sys
import time
import serial
import smtplib
import picamera
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
gateServoPin,alarmPin, irPin = 27,18, 24
GPIO.setup(alarmPin, GPIO.OUT)
GPIO.setup(gateServoPin, GPIO.OUT)
GPIO.setup(irPin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.output(alarmPin, GPIO.HIGH)
GPIO.output(gateServoPin, GPIO.HIGH)


# defining class for serial devices(GSM OR GPS)
class write_serial_device:
    global port
    global rcv
    rcv = ""
    
    def __init__(self, serialDevice):

        """INITIALIZES THE CLASS AND SERIAL PORT(whether gsm or gps) WHEN OBJECT IS CREATED"""
        self.serialDevice = serialDevice
        print("connecting to %s..." %self.serialDevice)

        if self.serialDevice == "GSM":
            self.port = serial.Serial("/dev/ttyUSB1", baudrate = 9600, timeout = 20)
            lcd.lcd_string("%s INITIALIZED....." %serialDevice, LCD_LINE_2)
        elif self.serialDevice == "RFID":
            self.port1 = serial.Serial("/dev/ttyUSB0", baudrate = 9600, timeout = 2)
            lcd.lcd_string("%s INITIALIZED....." %serialDevice, LCD_LINE_1)
        
    def write_port(self, command, readByte, sleepTime):

        """ WRITES COMMAND TO THE ABOVE SELECTED PORT """
        self.port.write(command+"\r")
        rcv = self.port.read(readByte)
        print (rcv)
        time.sleep(sleepTime)        

    def call(self, mobNum):
        
        """ PLACES A CALL TO A SPECIFIED NO PASSED IN THE ARGUMENT """
        self.write_port("ATD+91%s;" %mobNum ,20,10)

    def send_msg(self, mobNum, message):

        """ SENDS THE MESSAGE TO THE SPECIFIED NO. AS PER THE ARGUMENT PASSED"""
        #command = "AT+CGMS"+ mobNum
        self.write_port("AT+CGMS=%s" % mobNum, 10, 1)
        self.write_port("message",10,2)

    def rfid(self):
        global port1,tag
        tag = ["0900711DDFBA"]
        
        rcv = self.port1.read(12)
        print rcv
        #return rcv
        time.sleep(1)
        rf = False
        for i in range(len(tag)):
            if rcv == tag[i]:
                print "welcome ankit mishra"
                rf = True
                return rf
        

# CREATING CLASS FOR KEYPAD
class myKeypad:

    """ DEFINING SOME GLOBAL VARIABLES """
    global COL
    global ROW
    global MATRIX
    
    ROW = [20,16,12,26]
    COL = [19,13,6,5]
    MATRIX = [
                ['1','2','3','A'],
                ['4','5','6','B'],
                ['7','8','9','C'],
                ['*','0','#','D']
            ]

    """ SETTING PINS OF ROWS AND COLUMN FOR KEYPAD TO BE OUTPUT"""
    for pin in ROW,COL:
        GPIO.setup(pin, GPIO.IN, pull_up_down= GPIO.PUD_UP)

    """ INITIALISES CLASS myKeypad """
    def __init__(self,purpose):
        self.purpose = purpose
        print("keypad object created for %s" % self.purpose)
        lcd.lcd_string("KEYPAD INITIALIZED..", LCD_LINE_3)

    """ READS THE KEY PRESS AND RETURNS THE KEY PRESSED """    
    def keypad(self):
        for j in range(4):
            GPIO.setup(COL[j], GPIO.OUT)
            GPIO.output(COL[j], 0)
            ch=0
            for i in range(4):
                if GPIO.input(ROW[i])==0:
                    ch=MATRIX[i][j]
             
                    print( "Key Pressed is %s:" %ch)
                    time.sleep(0.25)
                    return ch
                    while (GPIO.input(ROW[i]) == 0):
                        pass
            GPIO.output(COL[j],1)

class my_lcd:


    global LCD_WIDTH, LCD_CHR, LCD_CMD, LCD_LINE_1, LCD_LINE_2,LCD_LINE_3, LCD_LINE_4,E_PULSE,E_DELAY
    LCD_WIDTH, LCD_CHR, LCD_CMD,LCD_LINE_1, LCD_LINE_2,LCD_LINE_3, LCD_LINE_4, E_PULSE, E_DELAY = 20, True, False,0x80 ,0xC0,0x94,0xD4,0.0005,0.0005

    def __init__(self, pin_rs, pin_e, pins_db):
        
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        
        GPIO.setup(self.pin_e, GPIO.OUT)  
        GPIO.setup(self.pin_rs, GPIO.OUT)  
        for pin in self.pins_db:  
            GPIO.setup(pin, GPIO.OUT)  
        self.lcd_init()
        self.lcd_clear()

    
    def lcd_init(self):
        global command
        
        command=[0x33,0x32,0x06,0x0C,0x01]
        for i in range(len(command)):
            self.lcd_byte(command[i], LCD_CMD)
        
        time.sleep(E_DELAY)
        self.lcd_string("LCD INITIALIZED....", LCD_LINE_1)
        time.sleep(1)

    def lcd_clear(self):

        self.lcd_byte(0x01, LCD_CMD)

    def lcd_byte(self,bits,mode):
        """ Send command to LCD """  
  
        time.sleep(0.0005)  
        bits=bin(bits)[2:].zfill(8)          
        GPIO.output(self.pin_rs, mode)  
  
        for pin in self.pins_db:  
            GPIO.output(pin, False)  
  
        for i in range(4):  
            if bits[i] == "1":  
                GPIO.output(self.pins_db[::-1][i], True)  
  
        self.lcd_toggle_enable()
        
        for pin in self.pins_db:  
            GPIO.output(pin, False)  
  
        for i in range(4,8):  
            if bits[i] == "1":  
                GPIO.output(self.pins_db[::-1][i-4], True)  

        self.lcd_toggle_enable()
  
        
    def lcd_toggle_enable(self):
        # Toggle enable
        time.sleep(E_DELAY)
        GPIO.output(self.pin_e, True)
        time.sleep(E_PULSE)
        GPIO.output(self.pin_e, False)
        time.sleep(E_DELAY)

    def lcd_string(self,message,line):
        # Send string to display
         
        message = message.ljust(LCD_WIDTH," ")
         
        self.lcd_byte(line, LCD_CMD)
         
        for i in range(LCD_WIDTH):
            self.lcd_byte(ord(message[i]),LCD_CHR)

class cam:
    
    def __init__(self,purpose):
        """ INITIALIZES THE CLASS CAM"""
        global camera
        self.purpose = purpose
        camera = picamera.PiCamera()        
        camera.rotation = 180
        print("camera initialization for security")
        lcd.lcd_string("CAMERA INITIALIZED..", LCD_LINE_4)
        

    def image(self, location):

        """ CLICKS IMAGES AT THW SPECIFIED LOCATION """
        camera.start_preview()
        time.sleep(2) # hang for preview for 5 seconds
        camera.capture(location)
        camera.stop_preview()
        print("image captured at %s" %location)

    def video(self, name, time, location):

        """ RECORDS VIDEO AT THE SPECIFIED LOCATION """
        camera.start_preview()
        camera.start_recording('/home/pi/video.h264')
        time.sleep(10)
        camera.stop_recording()
        camera.stop_preview()
        print("video captured at %s" %location)

    def stop(self):
        """ STOPS THE CAMERA TO CAPTURE ANYTHING"""        
        camera.close()
        
# DEFINE FUNCTION TO SEND ATTACHMENTS TO EMAIL    
def send(purpose):
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.MIMEBase import MIMEBase
    from email import encoders
     
    fromaddr = "amishm766@gmail.com"
    toaddr = "am9713490290@gmail.com"
     
    msg = MIMEMultipart()
     
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = purpose
     
    body = "Your security has been breached"
     
    msg.attach(MIMEText(body, 'plain'))
     
    filename = "/var/www/html/image.jpg"
    attachment = open(filename, "rb")
     
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
     
    msg.attach(part)    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "amishm766@")
    print("logging in to %s" %fromaddr)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    print("sending email to %s" % toaddr) 
    server.quit()
    print("email sent to %s" % toaddr)

# DEFINES THE MAIN PROGRAM WHICH COMPARES PIN ENTERED WITH THE REGISTERED PIN 
def lock():
    n,t=0,0    
    while True:
                
        PIN =[]
        tag = ["0900711DDFBA"]
        if GPIO.input(irPin) == 0:
            check = True
            lcd.lcd_string("Enter pin to", LCD_LINE_3)
            lcd.lcd_string("open the gate", LCD_LINE_4)            
            while check:

                """ CHECK FOR THE KEYPRESS TILL KEYBOARDINTERRUPT OR check = False"""
                key = 0
                key = sec.keypad()
                if key:

                    """ IF ANY KEY IS PRESSED INTER THIS LOOP(key >0) """
                    if key == '#':

                        """ IF # IS PRESSED ENTER HERE AND CHECK WHETHER PIN IS CORRECT"""
                        pin =0
                        pin= ''.join(PIN)
                        if pin == "1234":

                            """ ENTER HERE IF THE PIN IS CORRECT """
                            lcd.lcd_string("PUNCH YOUR ID CARD", LCD_LINE_1)
                            while check:
                                ch = rfid_tag.rfid()                        
                                if ch :
                                    print("tag found")
                                    GPIO.output(gateServoPin, GPIO.LOW)
                                    time.sleep(3)
                                    GPIO.output(gateServoPin, GPIO.HIGH)
                                    print("OPENING THE GATE")
                                    lcd.lcd_string("PUSH GATE TO OPEN", LCD_LINE_1)
                                    time.sleep(2)
                                    myCam.image('/var/www/html/image.jpg')
                                    send("correct pin")
                                    lcd.lcd_clear()
                                    check = False
                                else:
                                    print("not identified")

                        elif pin == "4321":

                            """ IF THE PIN ENTERED IS REVERSE OF REGISTERD PIN, CALL POLICE """
                            lcd.lcd_string("WAIT CHECKING PIN...", LCD_LINE_1)
                            myCam.image('/var/www/html/image.jpg')
                            calling.call("9713490290")
                            GPIO.output(gateServoPin, GPIO.LOW)
                            time.sleep(3)
                            GPIO.output(gateServoPin, GPIO.HIGH)
                            lcd.lcd_string("PUSH GATE TO OPEN", LCD_LINE_1)
                            time.sleep(2)
                            lcd.lcd_clear()
                            send("security breach")
                            check = False
                            
                        else:
                            
                            """ IF PIN IS INCORRECT CALL THE HOUSE OWNER """
                            lcd.lcd_clear()
                            lcd.lcd_string("wrong pin try again!", LCD_LINE_1)                    
                            lcd.lcd_string(" %d ATTEMPTS LEFT" % (5-n-1), LCD_LINE_2)
                            GPIO.output(alarmPin, GPIO.LOW)
                            myCam.image('/var/www/html/image.jpg')                           
                            #calling.call("9713490290")
                            GPIO.output(alarmPin, GPIO.HIGH)
                            #send("wrong pin")
                            lcd.lcd_clear()                                                    
                            if n == 4:
                                """ IF NO, OF ATTEMPTS EQUAL TO 5 ENTER HERE """
                                lcd.lcd_clear()
                                lcd.lcd_string("OVER LIMIT FOR TODAY ", LCD_LINE_1)                                
                                while check:
                                    if t < 10:
                                        """ MAKE USER WAIT FOR 10 SECONDS """
                                        lcd.lcd_string("TIME LEFT : %d" %(10-t), LCD_LINE_2)
                                        t+=1
                                        time.sleep(1)
                                    else:
                                        n = 0
                                        t = 0
                                        lcd.lcd_clear()
                                        check = False
                            else:
                                check = False
                                n = n+1
                            
                    else:

                        """ ADD KEYS PRESSED TO PIN AND DISPLAY ON LCD """
                        PIN+=key
                        lcd.lcd_byte(ord(key),LCD_CHR)
                        time.sleep(0.25)
                        print("PIN is %s" % "".join(PIN))

        else:
            print("nobody is there")
            time.sleep(1)


if __name__ == '__main__':
    try:
        """ FIRSTLY INITIALISE LCD AND THEN CREATE OBJECTS AND CALL MAIN[lock()] FUNCTION """
        #count = False
        lcd = my_lcd(22,11,[23,10,9,25])
        rfid_tag = write_serial_device("RFID")
        calling = write_serial_device("GSM")        
        myCam = cam("security")
        sec = myKeypad("security")
                
        time.sleep(2)
        lcd.lcd_clear()
        
        lock()
    except KeyboardInterrupt:
        print("exiting the program")
        lcd.lcd_clear()
        lcd.lcd_string("GOODBYE !!!", LCD_LINE_1)
        time.sleep(2)

    finally:
        lcd.lcd_clear()
        #myCam.stop()
        GPIO.cleanup()
