#!/usr/bin/env python

import sys
import socket
import time
import logging
import threading

logger = logging.getLogger('SERVER')
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler('irobot.log')
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)
from irobot import IRobot


# listen to port
# HOST = socket.gethostname()
HOST = 'localhost'
PORT = 50007

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

robot = IRobot()


def log_sensors():
    global robot
    
    logger.info('Send REQ SENSOR "ALL" to ROBOT')
    logger.info('Receive RESP "' + (';'.join(robot.combined_sensors())) + '" for REQ "ALL" from ROBOT')


# save sensor data every 35ms
#set_interval(log_sensors, 0.035)

def log_request(message):
    logger.info('Receive REQ CMD "' + message + '" from CLIENT');
    logger.info('Send REQ CMD "' + message + '" to ROBOT');


while True:
    print 'Waiting for a connection'
    conn, addr = s.accept()
    print "connection received"
    
    try:
        message = conn.recv(1024)
        args = message.split(';SEP;')
        
        # check if one action argument is given
        if (len(args) < 1):
            msg = 'Missing parameter: Please add at least one argument for running'
            logger.warn(msg)
            print msg
            continue
        
        action = args[0]
        
        # set finished flag which shows if an event, like go left ends
        logger.debug('Action argument: ' + str(action))
        logger.debug('Finished argument: ' + str(args[1]))
        if len(args) > 1:
            finished = args[1] == 'true' or args[1] == '1'
        else:
            finished = False
        
        output = 'n/a'
        request_action = None  # set action modes
	print "The action is " + action
        if (action == 'LEFT'):
            request_action = 'Robot goes left'
            log_request(request_action)
            output = robot.left(finished)
        if (action == 'RIGHT'):
            request_action = 'Robot goes right'
            log_request(request_action)
            output = robot.right(finished)
        if (action == 'GO' or action == 'STRAIGHT_FORWARD'):
            request_action = 'Robot goes straight forward'
            log_request(request_action)
            output = robot.straightForward(finished)
        if (action == 'TURN' or action == 'BACK'):
            request_action = 'Robot turns'
            log_request(request_action)
            output = robot.turn(finished)
        
        # set internal modes
        if (action == 'BEEP' or action == 'TOOT'):
            request_action = 'Robot toots'
            log_request(request_action)
            output = robot.beep()
        if (action == 'PASSIVE_MODE'):
            request_action = 'Robot changes to passive mode'
            log_request(request_action)
            output = robot.passive_mode()
        if (action == 'SAFE_MODE'):
            request_action = 'Robot changes to save mode'
            log_request(request_action)
            output = robot.safe_mode()
        if (action == 'DOCKING_MODE'):
            request_action = 'Robot changes to docking mode'
            log_request(request_action)
            output = robot.dock_mode()
        if (action == 'CLEANING_MODE'):
            request_action = 'Robot changes to cleaning mode'
            log_request(request_action)
            output = robot.clean_mode()
        if (action == 'FULL_MODE'):
            request_action = 'Robot changing to full control mode'
            log_request(request_action)
            output = robot.full_mode()
        if (action == 'RESET'):
            request_action = 'Robot resets'
            log_request(request_action)
            output = robot.reset()
        
        if (request_action is not None):
            logger.info('Receive RESP "' + str(output) + '" for REQ "' + request_action + '" from ROBOT')
            print "Output: " + str(output)
        else:
            logger.warn('Request could not be routed to any action, maybe invalid or unsupported action. ')

    except Exception as e:
        message = "Exception raised - close server"
        logger.warn(message)
        message2 = "Error: " + str(e)
        logger.warn(message2)
        
        conn.close()

