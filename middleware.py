#!/usr/bin/python

import socket               # Import socket module
import sys

if (len(sys.argv) <= 2):
	print "Please enter at least two arguments: action:String finished:Boolean or action:String message:String"
	sys.exit(1);

#s = socket.socket()         # Create a socket object
#host = socket.gethostname() # Get local machine name
HOST = '127.0.0.1'
PORT = 50007                # Reserve a port for your service.

message = str(sys.argv[1]) + ';SEP;' + str(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall(message)

s.close()                     # Close the socket when done
