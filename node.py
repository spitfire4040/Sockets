# header files
import socket
import sys
import _thread
#import SocketServer
import socketserver
import os
import time
import random
import pickle
import ast

# set global variables
NID = 0
hostname = ' '
udp_port = 0
tcp_port = 0
l1_NID = 0
l2_NID = 0
l3_NID = 0
l4_NID = 0
l1_hostname = ' '
l2_hostname = ' '
l3_hostname = ' '
l4_hostname = ' '
l1_udp_port = 0
l2_udp_port = 0
l3_udp_port = 0
l4_udp_port = 0
l1_tcp_port = 0
l2_tcp_port = 0
l3_tcp_port = 0
l4_tcp_port = 0
l1_flag = False
l2_flag = False
l3_flag = False
l4_flag = False

routes = {}

# create node object variable
node = None

# function: InitializeTopology
def InitializeTopology (nid, itc):

	# global variables
	global node

	# initialize node object
	node = Node(int(nid))

	# open itc.txt file and read to list
	infile = open(itc)
	list = infile.readlines()

	# initialize lists for hostnames and port numbers
	hostnames = []
	ports = []

	# populate hostname and port lists
	for entry in list:
		temp = entry.split(' ')
		hostnames.append(temp[1])
		ports.append(int(temp[2]))

	# use list to populate LinkTable and PortTable
	for entry in list:
		temp = entry.split(' ')
		node.Set_link_table(int(temp[0]), (int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6])))
		node.Set_address_data_table(int(temp[0]), temp[1], int(temp[2]))

		# set parameters for for this node
		if node.GetNID() == int(temp[0]):
			node.SetHostName(temp[1])
			node.SetPort(int(temp[2]))

			# set starting point
			number_of_nodes = len(temp) - 3
			index = 3

			# iterate through and add all links for this node
			for i in range(number_of_nodes):
				corresponding_hostname = hostnames[int(temp[index+i])-1]
				corresponding_port = ports[int(temp[index+i])-1]
				node.AddLink((int(temp[index+i]), corresponding_hostname, corresponding_port))

	# close itc.txt file
	infile.close()

	# return object
	return node

# class: Node
class Node(object):

	# initialize node
	def __init__ (self, nid=0, host_name=None, udp_port=0, links=[], address_data_table = [], link_table={}):
		self.nid = nid
		self.host_name = host_name
		self.udp_port = udp_port

		if links is not None:
			self.links = list(links)

		self.upL1 = False
		self.upL2 = False
		self.upL3 = False
		self.upL4 = False
		self.link_table = {}
		self.address_data_table = {}
    
	# get nid
	def GetNID (self):
		return self.nid

	# get hostname
	def GetHostName (self):
		return self.host_name

	# get port number
	def GetPort (self):
		return self.udp_port

	# get list of links
	def GetLinks (self):
		return self.links

	# get shutdown status
	def GetShutdownStatus (self):
		return self.shutdown

	# get link table (all links)
	def Get_link_table (self):
		return self.link_table

	# get port table (all ports)
	def Get_address_data_table (self):
		return self.address_data_table

	# get up flag for neighbor 1
	def GetUpFlagL1 (self):
		return self.upL1

	# get up flag for neighbor 2
	def GetUpFlagL2 (self):
		return self.upL2

	# get up flag for neighbor 1
	def GetUpFlagL3 (self):
		return self.upL3

	# get up flag for neighbor 2
	def GetUpFlagL4 (self):
		return self.upL4    

	# set up flag for neighbor 1
	def SetUpFlagL1 (self, flag):
		self.upL1 = flag

	# set up flag for neighbor 2
	def SetUpFlagL2 (self, flag):
		self.upL2 = flag

	# set up flag for neighbor 1
	def SetUpFlagL3 (self, flag):
		self.upL3 = flag

	# set up flag for neighbor 2
	def SetUpFlagL4 (self, flag):
		self.upL4 = flag

	# set nid
	def SetNID (self, nid):
		self.nid = nid

	# set hostname
	def SetHostName (self, host_name):
		self.host_name = host_name

	# set port number
	def SetPort (self, udp_port):
		self.udp_port = udp_port

	# add link to links list
	def AddLink (self, individual_link):
		self.links.append(individual_link)

	# set link table
	def Set_link_table (self, source_nid, neighbor_nid):
		self.link_table[source_nid] = neighbor_nid
		#pass

	# set port table
	def Set_address_data_table (self, nid, hostname, port):
		self.address_data_table[nid] = nid, hostname, port

# class TCP Handler
class MyTCPHandler(socketserver.BaseRequestHandler):

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port
	global l1_NID, l2_NID, l3_NID, l4_NID

	neighbor_list = [l1_NID,l2_NID,l3_NID,l4_NID]	

	def handle(self):

		self.data = self.request.recv(1024)
		message = pickle.loads(self.data)
		message = message.split()

######################################## Print or Forward Messages #############################################

		# if message[0] == 'msg':
		# 	print message[1]
		# 	print '\r'























#################################################################################################################

######################################### Update Routing Tables #################################################			

		if message[0] == 'rte':
			temp_routes = ast.literal_eval(''.join(message[1:]))

			# if it's in temp_routes but not in routes, add it to routes
			for temp_route in temp_routes:
				if temp_route not in routes:
					routes[temp_route] = (temp_routes[temp_route][0],temp_routes[temp_route][1])

			# if it's not in temp_routes but it is in routes, delete it from routes
			for route in routes:
				if route not in temp_routes:
					del routes[route]

		# output both lists for testing
		print(str(NID) + ' has these routes: ' + str(routes))




















#################################################################################################################

# Class: MyUDPHandler
#class MyUDPHandler(SocketServer.BaseRequestHandler):
class MyUDPHandler(socketserver.BaseRequestHandler):

	# interrupt handler for incoming messages
	def handle(self):

		# global variables
		global udp_port, l1_udp_port, l2_udp_port, l3_udp_port, l4_udp_port, l1_flag, l2_flag, l3_flag, l4_flag

		# parse received data
		data = self.request[0].strip()

		# set message and split
		message = pickle.loads(data)
		message = message.split()

		# set link flags
		if message[2] == str(l1_udp_port):
			l1_flag = True

		if message[2] == str(l2_udp_port):
			l2_flag = True

		if message[2] == str(l3_udp_port):
			l3_flag = True

		if message[2] == str(l4_udp_port):
			l4_flag = True          

# Function: sendto()
def sendto(dest_nid, message):

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port	
	global l1_NID, l2_NID, l3_NID, l4_NID

################################# Send Message to Neighbor that is In The Network ####################################




















#######################################################################################################################

	# Create a socket (SOCK_STREAM means a TCP socket)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		print('sending ' + '"' + message + '"' + ' to ' + l1_hostname + ', ' + str(l1_udp_port) + ' ' + str(l1_tcp_port))
		# Connect to server and send data
		sock.connect((l1_hostname, l1_tcp_port))
		sock.sendall('msg' + ' ' + message)

		# Receive data from the server and shut down
		received = sock.recv(1024)
	finally:
		sock.close()

# function: start listener
def start_listener():

	# global variables
	global node, NID, hostname, udp_port, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_udp_port, l2_udp_port, l3_udp_port, l4_udp_port
	global l1_tcp_port, l2_tcp_port, l3_tcp_port, l4_tcp_port	
	global l1_NID, l2_NID, l3_NID, l4_NID

	# check links for node attributes
	links = node.GetLinks()
	link1 = links[0]
	link2 = links[1]
	link3 = links[2]
	link4 = links[3]

	l1_NID = link1[0]
	l1_hostname = link1[1]
	l1_udp_port = link1[2]
	l1_tcp_port = l1_udp_port + 500

	l2_NID = link2[0]
	l2_hostname = link2[1]
	l2_udp_port = link2[2]
	l2_tcp_port = l2_udp_port + 500

	l3_NID = link3[0]
	l3_hostname = link3[1]
	l3_udp_port = link3[2]
	l3_tcp_port = l3_udp_port + 500

	l4_NID = link4[0]
	l4_hostname = link4[1]
	l4_udp_port = link4[2]
	l4_tcp_port = l4_udp_port + 500

	hostname = node.GetHostName()
	NID = node.GetNID()
	udp_port = node.GetPort()
	tcp_port = udp_port + 500

	# slight pause to let things catch up
	time.sleep(2)

	# start threads for listener
	try:
		_thread.start_new_thread(TCP_listener, ())
	except:
		print('failed to call TCP_listener thread')

	try:
		_thread.start_new_thread(UDP_listener, ())
	except:
		print('failed to cass UDP_listener thread')

	try:
		_thread.start_new_thread(hello, ())
	except:
		print('failed to call hello thread')

	try:
		_thread.start_new_thread(timer, ())
	except:
		print('failed to call timer thread')

	try:
		_thread.start_new_thread(routing, ())
	except:
		print('failed to call routing thread')

# function: TCP listener
def TCP_listener():

	# global variables
	global hostname, tcp_port

	# set socket for listener
	try:
		server = socketserver.TCPServer((hostname, tcp_port), MyTCPHandler)
		server.serve_forever()
	except:
		print("failed to start tcp listener")

# function: receiver (listener)
def UDP_listener():

 	# global variables
	global hostname, udp_port

	# set socket for listener
	try:
		server = socketserver.UDPServer((hostname, udp_port), MyUDPHandler)
		server.serve_forever()

	# report error if fail
	except:
		print("failed to start udp listener")

# function: hello (alive)
def hello():

	# global variables
	global NID, hostname, udp_port
	global l1_hostname, l2_hostname, l3_hostname,l4_hostname
	global l1_udp_port, l2_udp_port, l3_udp_port, l4_udp_port

	# eternal loop
	while (1):
		# pickle message
		message = pickle.dumps(str(NID) + ' ' + hostname + ' ' + str(udp_port))

		try:
			# open socket and send to neighbor 1
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0) # UDP
			sock.sendto(message, (l1_hostname, l1_udp_port))
			time.sleep(.5)
		except:
			print('did not send hello to ' + str(l1_udp_port))
			pass

		try:
			# open socket and send to neighbor 2
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0) # UDP
			sock.sendto(message, (l2_hostname, l2_udp_port))
			time.sleep(.5)
		except:
			print('did not send hello to ' + str(l2_udp_port))			
			pass

		try:
			# open socket and send to neighbor 3
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0) # UDP
			sock.sendto(message, (l3_hostname, l3_udp_port))
			time.sleep(.5)
		except:
			print('did not send hello to ' + str(l3_udp_port))						
			pass

		try:
			# open socket and send to neighbor 4
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0) # UDP
			sock.sendto(message, (l4_hostname, l4_udp_port))
			time.sleep(.5)
		except:
			print('did not send hello to ' + str(l4_udp_port))			
			pass

# function: timer (for hello)
def timer():

	# global variables 
	global node, l1_flag, l2_flag, l3_flag, l4_flag

	# # initialize flags to false, then wait 15 seconds to recheck
	l1_flag = False
	l2_flag = False
	l3_flag = False
	l4_flag = False

	time.sleep(3)

	# if true flag found, set neighbor 1 up flag
	if l1_flag == False:
		node.SetUpFlagL1(False)
	if l1_flag == True:
		node.SetUpFlagL1(True)

	# if true flag found, set neighbor 2 flag
	if l2_flag == False:
		node.SetUpFlagL2(False)
	if l2_flag == True:
		node.SetUpFlagL2(True)

	# if true flag found, set neighbor 3 flag
	if l3_flag == False:
		node.SetUpFlagL3(False)
	if l3_flag == True:
		node.SetUpFlagL3(True)

	# if true flag found, set neighbor 4 flag
	if l4_flag == False:
		node.SetUpFlagL4(False)
	if l4_flag == True:
		node.SetUpFlagL4(True)

	# eternal loop
	while (1):

		# initialize flags to false, then wait 15 seconds to recheck
		l1_flag = False
		l2_flag = False
		l3_flag = False
		l4_flag = False

		time.sleep(3)		

		# if true flag found, set neighbor 1 up flag
		if l1_flag == False:
			node.SetUpFlagL1(False)
		if l1_flag == True:
			node.SetUpFlagL1(True)

		# if true flag found, set neighbor 2 flag
		if l2_flag == False:
			node.SetUpFlagL2(False)
		if l2_flag == True:
			node.SetUpFlagL2(True)

		# if true flag found, set neighbor 3 flag
		if l3_flag == False:
			node.SetUpFlagL3(False)
		if l3_flag == True:
			node.SetUpFlagL3(True)

		# if true flag found, set neighbor 4 flag
		if l4_flag == False:
			node.SetUpFlagL4(False)
		if l4_flag == True:
			node.SetUpFlagL4(True)

		# now check for true every 15 seconds
		time.sleep(15)			

# function: routing
def routing():

	# <DESTINATION> <GATEWAY> <HOPS>
	#       2           4       3

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port	
	global l1_NID, l2_NID, l3_NID, l4_NID
	global l1_flag, l2_flag, l3_flag, l4_flag

	addresses = [(l1_NID,l1_hostname,l1_tcp_port),(l2_NID,l2_hostname,l2_tcp_port),(l3_NID,l3_hostname,l3_tcp_port),(l4_NID,l4_hostname,l4_tcp_port)]

	# start loop
	while(1):

		# write initial connections to file
		if node.GetUpFlagL1() == True:
			if l1_NID != 0:
				if l1_NID not in routes:
					routes[l1_NID] = (l1_NID,0)
		else:
			if l1_NID in routes:
				del routes[l1_NID]

		if node.GetUpFlagL2() == True:
			if l2_NID != 0:
				if l2_NID not in routes:
					routes[l2_NID] = (l2_NID,0)
		else:
			if l2_NID in routes:
				del routes[l2_NID]

		if node.GetUpFlagL3 == True:
			if l3_NID != 0:
				if l3_NID not in routes:
					routes[l3_NID] = (l3_NID,0)
		else:
			if l3_NID in routes:
				del routes[l3_NID]

		if node.GetUpFlagL4 == True:
			if l4_NID != 0:
				if l4_NID not in routes:
					routes[l4_NID] = (l4_NID,0)
		else:
			if l4_NID in routes:
				del routes[l4_NID]

		# update routes in all neighbor nodes
		#print(str(routes))
		message = pickle.dumps('rte' + ' ' + str(routes))

		for address in addresses:
			if address[0] == 0:
				pass
			else:
				try:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)				
					sock.connect((address[1], address[2]))
					sock.sendall(message)
				
					sock.close()
				except:
					continue

		# send this information every 30 seconds
		time.sleep(10)

# print status
def PrintStatus():

	# global variables
	global node, NID, hostname, udp_port, tcp_port

	os.system('clear')
	print("Status of this node")
	print("-------------------")
	print("NID: " + str(NID))
	print("HostName: ",)
	print("UDP Port: " + str(udp_port))
	print("TCP Port: " + str(tcp_port))

	print("Links: " + str(node.GetLinks()))
	print("Link Table: ", str(node.Get_link_table()))
	if l1_NID != 0:
		print("Link up to node " + str(l1_NID) + ':', (node.GetUpFlagL1()))
	if l2_NID != 0:
		print("Link up to node " + str(l2_NID) + ':', (node.GetUpFlagL2()))
	if l3_NID != 0:
		print("Link up to node " + str(l3_NID) + ':', (node.GetUpFlagL3()))
	if l4_NID != 0:
		print("Link up to node " + str(l4_NID) + ':', (node.GetUpFlagL4()))		
	print("Address Data Table: ", str(node.address_data_table))
	print("Routes from " + str(NID) + ": ", routes)
	print("-------------------")
	input("press 'enter' to continue....")

# main function
def main(argv):

	# global variables
	global node

	# set initial value for loop
	run = 1

	# check for command line arguments
	if len(sys.argv) != 3:
		print("Usage: <program_file><nid><itc.txt>")
		exit(1)

	# initialize node object
	node = InitializeTopology(sys.argv[1], sys.argv[2])

	# start UDP listener
	start_listener()

	# loop
	while(run):

		# print menu options
		os.system('clear')
		print("Enter 'status' to check node status")
		print("Enter 'send' to message another node")
		print("Enter 'quit' to end program")

		# set selection value from user
		selection = input("Enter Selection: ")

		# selection: status
		if selection == 'status':
			PrintStatus()

		# selection: send
		elif(selection == 'send'):
			os.system('clear')
			dest_node = input("enter the node you want to message: ")
			message = input("enter the message you want to send: ")
			sendto(dest_node, message)
			input("press 'enter' to continue...")

		# selection: quit
		elif(selection == 'quit'):
			run = 0
			os.system('clear')

		else:

			# default for bad input
			os.system('clear')
			time.sleep(.5)
			continue

# initiate program
if __name__ == "__main__":
	main(sys.argv)
