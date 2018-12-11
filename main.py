# Script to Turn on BOSE Solo 20 when the TV is turned on.  Initial
# script just uses the AdaFruit IR Remote to send the Enter/Save
# command to toggle the BOSE for testing.  Goal is to have an IR
# Sensor to listen for Tivo Remote power on command.  Another input
# looks for the BOSE power state by whether or not we see 5V on the
# USB output on the BOSE.  The third Pin sends the IR commands via an
# LED.
#
# Base module is a GemmaM0, which is just awesome!
#
# Author:  John Stoffel
# Date:    2018/03/06
#
# Pin A2/D0 - IR LED output
# Pin A0/D1 - Bose USB Power sense
# Pin A1/D2 - Sony TV USB Power sense

import board
import busio
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
import time
import adafruit_DotStar as dotstar

# IR send/decode base
import IRrecvPCI
# Basic NEC IR control codes. 
import IRLib_P01_NECd
import IRLib_P01_NECs

# Status via DotStar on GemmaM0
# Red - listening
# Blue - got a command
# Green  - sending BOSE Power Command
dot = busio.SPI(board.APA102_SCK, board.APA102_MOSI)

def setPixel(red, green, blue):
    if not dot.try_lock():
        return
    # print("setting pixel to: %d %d %d" % (red, green, blue))
 
    data = bytearray([0x00, 0x00, 0x00, 0x00,
                      0xff, blue, green, red,
                      0xff, 0xff, 0xff, 0xff])
    dot.write(data)
    dot.unlock()
    time.sleep(0.01)

# BOSE Solo 20 PowerOn/Off toggle command
BoseAddr = 0x5
BoseData = 0xd0532cd

# IR send
# myS = IRLib_P07_NECxs.IRsendNECx(board.D0)
myS = IRLib_P01_NECs.IRsendNEC(board.D0)

#Power_BOSE = DigitalInOut(board.D2)
#Power_BOSE.direction = Direction.INPUT
#Power_BOSE.pull = Pull.DOWN
Power_BOSE = AnalogIn(board.A1)

#Power_Sony = DigitalInOut(board.D1)
#Power_Sony.direction = Direction.INPUT
#Power_Sony.pull = Pull.DOWN
Power_Sony = AnalogIn(board.A0)

def getVoltage(pin):  # helper 
    return (pin.value * 3.3) / 65536

def gotPwr(pin):
    if getVoltage(pin) > 2.0:
        return True
    else:
        return False
    
# create instance on pin D2 on GemmaM0 board
# myR = IRrecvPCI.IRrecvPCI(board.D2)
# myR.enableIRIn()

# Decoder using NEC codes?
# myD = IRLib_P01_NECd.IRdecodeNEC()

print("Ready")
count = 0
#led.value = 0
setPixel(255,0,0)
while True:
    print("Sony Power = %1.2f, BOSE power = %1.2f" % (getVoltage(Power_Sony), getVoltage(Power_BOSE)))
    if getVoltage(Power_Sony) > 2.0:
        print("SONY TV is on, ",end='')
        setPixel(0,255,0)

        if getVoltage(Power_BOSE) < 1.0:
            print(" BOSE is off, sending command...")
            myS.send(BoseData,BoseAddr)
            time.sleep(.5)
            setPixel(0,0,0)
            time.sleep(0.5)
        else:
            print(" BOSE already On.")
            time.sleep(1)
    else:
        print("SONY TV is off! ",end='')
        setPixel(255,0,0)
        if getVoltage(Power_BOSE) > 2.0:
            print(" Power down BOSE command...")
            myS.send(BoseData,BoseAddr)
            time.sleep(.5)
            setPixel(255,0,0)
            time.sleep(0.5)
        else:
            setPixel(255,0,0)
            print(" BOSE already off, sleeping...")
            time.sleep(1)
    time.sleep(1)
            
