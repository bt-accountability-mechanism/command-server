import struct
import os
import sys, glob # for listing serial ports
from random import randint

import logging
logger = logging.getLogger('SERVER')
dev_mode = os.getenv('TEST_IROBOT', '0') == '1'
if dev_mode == False:
    try:
        import serial
    except ImportError:
        logger.warn('Import error, please install pyserial.')
        raise

connection = None

VELOCITYCHANGE = 200
ROTATIONCHANGE = 300

class IRobot():
    # static variables for keyboard callback -- I know, this is icky
    _callbackKeyUp = False
    _callbackKeyDown = False
    _callbackKeyLeft = False
    _callbackKeyRight = False
    _callbackKeyLastDriveCommand = ''

    _port = '/dev/ttyUSB0'


    #####################################################
    ############# INTERNAL ACTIONS START ################
    #####################################################

    def beep(self):
        return self._callbackKey('2', 'SPACE')

    def input(self):
        return self._sendCommandASCII('142')

    def leftCliffSensorData(self): 
        return self._sendCommandASCII('148 1 9')

    # autonomous cleaning
    def clean_mode(self):
        return self._callbackKey('2', 'C')

    # full control over robot -> no safety
    def full_mode(self):
        return self._callbackKey('2', 'F')

    # do nothing
    def passive_mode(self):
        return self._callbackKey('2', 'P')

    # try to find loading station
    def dock_mode(self):
        return self._callbackKey('2', 'D')

    # full control with safety enabled
    def safe_mode(self):
        return self._callbackKey('2', 'S')

    # start irobot
    def start(self):
        # return 1
        return self._sendCommandASCII('128')

    # reboot
    def reset(self):
        return self._callbackKey('2', 'R')

    #####################################################
    ############# MOVEMENT ACTIONS START ################
    #####################################################
    def left(self, finish):
        return self._motion_action('LEFT', finish)

    def straightForward(self, finish):
        return self._motion_action('UP', finish)

    def right(self, finish):
        return self._motion_action('RIGHT', finish)

    def turn(self, finish):
        return self._motion_action('DOWN', finish)

    #####################################################
    ############# SENSOR ACTIONS START ################
    #####################################################

    def combined_sensors(self):
        self.connect()
        # cliff sensor left, front left, front right, right - wall sensor -  bump sensor - velocity - oi mode (0: off, 1: passive, 2: safe, 3: full)
        self._sendCommandASCII('149 9 9 10 11 12 8 29 7 39 35')
        cliff = [str(self._get8Unsigned()), str(self._get8Unsigned()), str(self._get8Unsigned()), str(self._get8Unsigned())]
        wall = self._get8Unsigned()
        bump = self._get8Unsigned()
        velocity = self._get16Signed()
        oi = self._get8Unsigned()
        # print "Wall: " + str(wall)
        # print "Bump: " + str(bump)
        # print "Velo: " + str(velocity)
        # print "OI: " + str(oi)
        return [','.join(cliff), str(wall), str(bump), str(velocity), str(oi)]

    ## cliff = 1, otherwise: no cliff
    def cliff(self):
        self._sendCommandASCII('149 4 9 10 11 12')
        reply = [self._get8Unsigned(), self._get8Unsigned(), self._get8Unsigned(), self._get8Unsigned()]
        if (reply[0] == 1 or reply[1] == 1 or reply[2] == 1 or reply[3] == 1): 
		return 1
	else:
		return 0

    ## returns battery temperature in C
    def battery_temp(self):
	# print "bat"
        output = self._sendCommandASCII('149 1 24')
        # print "command output: " + str(output)
        reply = self._get8Signed()
        # print "Bat value" + str(reply)
        return reply

    ## returns bumper code number: 0: no bumper, 1: right bumper, 2: left bumper, 3: both bumpers
    def bumper(self):
	# print "bump"
        self._sendCommandASCII('149 1 7')
	reply = self._get8Unsigned()
        return reply

    #####################################################
    ############# HELPER FUNCTIONS START ################
    #####################################################

    def _motion_action(self, key, finish):
        if finish:
            return self._callbackKey('3', key)
        else:
            return self._callbackKey('2', key)

    def connect(self):
        global connection

        if connection is not None:
            logger.debug("Device is already connected")
            return 1

        port = self._port

        if port is not None and dev_mode == False:
            logger.debug("Trying " + str(port) + "... ")
            try:
                connection = serial.Serial(port, baudrate=115200, timeout=1)
                self.start()
                logger.debug("Connection to port succeeded!")
                return 0
            except Exception as e:
                logging.exception("Failed, couldn't connect to " + str(port))
                return 2

    # getDecodedBytes returns a n-byte value decoded using a format string.
    # Whether it blocks is based on how the connection was set up.
    def _getDecodedBytes(self, n, fmt):
        global connection

        try:
            if dev_mode == False:
                read_output = connection.read(n)
                return struct.unpack(fmt, read_output)[0]
            else:
                return randint(0,10)
    
        except serial.SerialException:
            print "Lost connection"
            connection = None
            return None
        except struct.error as error:
            print "Got unexpected data from serial port." + str(error)
            return None

    # get8Unsigned returns an 8-bit unsigned value.
    def _get8Unsigned(self):
        return self._getDecodedBytes(1, "B")

    # get8Signed returns an 8-bit signed value.
    def _get8Signed(self):
        return self._getDecodedBytes(1, "b")

    # get16Unsigned returns a 16-bit unsigned value.
    def _get16Unsigned(self):
        return self._getDecodedBytes(2, ">H")

    # get16Signed returns a 16-bit signed value.
    def _get16Signed(self):
        return self._getDecodedBytes(2, ">h")

    # sendCommandRaw takes a string interpreted as a byte array
    def _sendCommandRaw(self, command):
        global connection

        try:
            if connection is not None:
                output = connection.write(command);
                #logger.debug("Output in hex: %s", hex(output))
                #logger.debug("Output of writing: %s", output)
                logger.debug('Write command %s to robot successful', command)
                return 0
            elif dev_mode == False:
                logger.warn("No connection to device available")
                return 2
            else:
                return 1
        except serial.SerialException:
            logger.debug("Lost connection to robot")
            return 1

    # sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
    def _sendCommandASCII(self, command):
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        logger.debug('Send command %s', cmd)

        return self._sendCommandRaw(cmd)

    # A handler for keyboard events. Feel free to add more!
    def _callbackKey(self, key_type, key_value):
        # first: connect to device
        connect = self.connect()
        # check if connection was successful
        if (connect > 1):
            logger.debug("Connection to device failed")
            return 2

        k = key_value.upper()
        motionChange = False

        # error: no output variable passed in
        output = 10

        if key_type == '2': # KeyPress; need to figure out how to get constant
            if k == 'P':   # Passive
                output = self._sendCommandASCII('128')
            elif k == 'S': # Safe
                output = self._sendCommandASCII('131')
            elif k == 'F': # Full
                output = self._sendCommandASCII('132')
            elif k == 'C': # Clean
                output = self._sendCommandASCII('135')
            elif k == 'D': # Dock
                output = self._sendCommandASCII('143')
            elif k == 'SPACE': # Beep
                print 'Send beep command'
                output = self._sendCommandASCII('140 3 1 64 16 141 3')
            elif k == 'R': # Reset
                output = self._sendCommandASCII('7')
            elif k == 'UP':
                self._callbackKeyUp = True
                motionChange = True
            elif k == 'DOWN':
                self._callbackKeyDown = True
                motionChange = True
            elif k == 'LEFT':
                self._callbackKeyLeft = True
                motionChange = True
            elif k == 'RIGHT':
                self._callbackKeyRight = True
                motionChange = True
            else:
                print repr(k), "not handled"
                return 1
        elif key_type == '3': # KeyRelease; need to figure out how to get constant
            if k == 'UP':
                self._callbackKeyUp = False
                motionChange = True
            elif k == 'DOWN':
                self._callbackKeyDown = False
                motionChange = True
            elif k == 'LEFT':
                self._callbackKeyLeft = False
                motionChange = True
            elif k == 'RIGHT':
                self._callbackKeyRight = False
                motionChange = True

        if motionChange == True:
            velocity = 0
            velocity += VELOCITYCHANGE if self._callbackKeyUp is True else 0
            velocity -= VELOCITYCHANGE if self._callbackKeyDown is True else 0
            rotation = 0
            rotation += ROTATIONCHANGE if self._callbackKeyLeft is True else 0
            rotation -= ROTATIONCHANGE if self._callbackKeyRight is True else 0

            # compute left and right wheel velocities
            vr = velocity + (rotation/2)
            vl = velocity - (rotation/2)

            logger.debug("Velocity left wheel: %s", vl)
            logger.debug("Velocity right wheel: %s", vr)
            logger.debug("Rotation: %s", rotation)

            # create drive command
            cmd = struct.pack(">Bhh", 145, vr, vl)
            if cmd != self._callbackKeyLastDriveCommand:
                output = self._sendCommandRaw(cmd)
                self._callbackKeyLastDriveCommand = cmd

        return output

