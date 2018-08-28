# Libraries
import sys
import os
import thread
import SocketServer
import socket
import time


# UDP handler class
class MyUDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):

    	# parse and print received data
        data = self.request[0].strip()
        #socket = self.request[1]
        # clear the screen before
        os.system('clear')
        print '\r' + self.client_address[0] + ' wrote: {' + data + '}' + '\r'

        # re-print prompt to screen (it got overwritten by incoming message)
        print "enter 1 to send a message, 0 to quit: "

def start_listener(hostIP, hostPort):
	# create a thread to run listener in the background
	thread.start_new_thread(receiver, (hostIP, hostPort))


def receiver(hostIP, hostPort):
	# attempt to start listener
	try:
		# print port i'm listening on
		print "Listening on port " + hostPort

		# build socket
		server = SocketServer.UDPServer((hostIP, int(hostPort)), MyUDPHandler)

		# run socket forever
		server.serve_forever()

	# give error message if it doesn't start
	except:
	 	print("failed to start listener")


def send_message(destIP, destPort, message):
	# initialize variables
	HOST = destIP
	PORT = destPort
	data = message

	# create socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# send message
	sock.sendto(data, (HOST, int(PORT)))


def main(args):
	# clear the screen
	os.system('clear')

	# initialize run variable
	run = '1'

	# check for proper command line input
	if(len(args) < 3):
		print("USAGE: <program name> <host ip> <host port> i.e. 'node.py 127.0.0.1 50001'")
	else:
		hostIP = sys.argv[1]
		hostPort = sys.argv[2]

		# start the listener
		start_listener(hostIP, hostPort)

		# wait for 1 second for things to print to screen
		time.sleep(1)

	# loop
	while(run == '1'):
		# short delay so stuff isn't overwritten
		time.sleep(1)

		# prompt for user input
		command = raw_input("enter 1 to send a message, 0 to quit: ")
		if(command == '1'):

			os.system('clear')

			IP = raw_input("enter destination IP address: ")
			PORT = raw_input("enter destination port number: ")
			message = raw_input("enter message to send: ")
			send_message(IP, PORT, message)
		else:
			run = 0


# call main function to start program
if __name__ == '__main__':
	main(sys.argv)