# header files
import socket
import sys
import threading
from threading import Thread
import socketserver
import os
import time
import random
import pickle
import ast
from random import randint

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
temp_routes = {}

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

	def handle(self):

		# global variables
		global NID, hostname, tcp_port
		global l1_hostname, l2_hostname, l3_hostname, l4_hostname
		global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port
		global l1_NID, l2_NID, l3_NID, l4_NID

		self.data = self.request.recv(1024)
		message = pickle.loads(self.data)
		message = message.split()

		if message[0] == 'msg':
			target = int(message[1])
			source = message[2]
			hops = int(message[3])
			package = ''.join(message[4:])

			if target == NID:
				os.system('clear')
				print(source + ' says: ' + package)
				os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

			else:
				hops -= 15
				sendto(target, package, hops)
				print('forwarding...')

		# if the first part of the incoming message is 'rte'
		if message[0] == 'rte':

			# set neighbor_node id variable to keep track of where update came from
			NNID = message[1]

			# convert the rest of the string back to a dictionary
			temp_routes = ast.literal_eval(''.join(message[2:]))

			# iterate through incoming dictionary (temp_routes)
			for item in temp_routes:

				# if temp_route is not in routes, and the NID of the new route isn't my NID (no routes to myself)
				if item not in routes and item != NID:

					# add the route, set the gateway to the neighbor it came from, and increment hops by 1
					routes[item] = (NNID,(temp_routes[item][1]+1))

				# if temp_route is in routes already
				if item in routes:

					# if the hop count of the new route is smaller than the hop count of the current route, and the route isn't to me
					if temp_routes[item][1] < routes[item][1]:

							# update routes with new shorter route
							routes[item] = (NNID, (temp_routes[item][1]+1))

			try:
				for item in routes:

					if item not in temp_routes:

						del routes[item]
			except:
				pass

# Class: MyUDPHandler
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
def sendto(dest_nid, hops, message):

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port	
	global l1_NID, l2_NID, l3_NID, l4_NID
	gateway = 0

	if dest_nid in routes:
		gateway = int(routes[dest_nid][0])

		if gateway == l1_NID:
			HOST = l1_hostname
			PORT = l1_tcp_port

		elif gateway == l2_NID:
			HOST = l2_hostname
			PORT = l2_tcp_port

		elif gateway == l3_NID:
			HOST = l3_hostname
			PORT = l3_tcp_port

		elif gateway == l4_NID:
			HOST = l4_hostname
			PORT = l4_tcp_port

		else:
			print('no address information for gateway ' + str(gateway))

	else:
		print(str(routes))
		print('No route to host, try again later.')


	package = pickle.dumps('msg' + ' ' + str(dest_nid) + ' ' + str(NID) + ' ' + str(hops) + ' ' + message)

	# Create a socket (SOCK_STREAM means a TCP socket)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# send route to neighbors
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)				
		sock.connect((HOST, PORT))
		sock.sendall(package)
		sock.close()

	except:
		print('unable to send message: HOST=' + HOST + ' , PORT=' + str(PORT))
		pass

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

	t1 = threading.Thread(target=TCP_listener)
	t1.daemon=True
	t1.start()

	t2 = threading.Thread(target=UDP_listener)
	t2.daemon=True
	t2.start()

	t3 = threading.Thread(target=hello)
	t3.daemon=True
	t3.start()

	t4 = threading.Thread(target=timer)
	t4.daemon=True
	t4.start()

	t5 = threading.Thread(target=local_routing)
	t5.daemon=True
	t5.start()

	t6 = threading.Thread(target=routing)
	t6.daemon=True
	t6.start()

# function: TCP listener
def TCP_listener():

	# global variables
	global hostname, tcp_port

	# set socket for listener
	server = socketserver.TCPServer((hostname, tcp_port), MyTCPHandler)
	server.serve_forever()

# function: receiver (listener)
def UDP_listener():

 	# global variables
	global hostname, udp_port

	# set socket for listener
	server = socketserver.UDPServer((hostname, udp_port), MyUDPHandler)
	server.serve_forever()

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

# function: local_routing
def local_routing():

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port	
	global l1_NID, l2_NID, l3_NID, l4_NID
	global l1_flag, l2_flag, l3_flag, l4_flag
	global update_flag_1, update_flag_2


	addresses = [(l1_NID,l1_hostname,l1_tcp_port),(l2_NID,l2_hostname,l2_tcp_port),(l3_NID,l3_hostname,l3_tcp_port),(l4_NID,l4_hostname,l4_tcp_port)]

	# start loop
	while(1):

		# check routes, add or edit;
		if node.GetUpFlagL1() == True:
			if l1_NID != 0:
				routes[l1_NID] = (l1_NID,1)

		else:
			if l1_NID in routes:
				del routes[l1_NID]

		# check routes, add or edit;
		if node.GetUpFlagL2() == True:
			if l2_NID != 0:
				routes[l2_NID] = (l2_NID,1)

		else:
			if l2_NID in routes:
				del routes[l2_NID]

		# check routes, add or edit;
		if node.GetUpFlagL3() == True:
			if l3_NID != 0:
				routes[l3_NID] = (l3_NID,1)

		else:
			if l3_NID in routes:
				del routes[l3_NID]

		# check routes, add or edit;
		if node.GetUpFlagL4() == True:
			if l4_NID != 0:
				routes[l4_NID] = (l4_NID,1)

		else:
			if l4_NID in routes:
				del routes[l4_NID]

		# send this information every 15 seconds
		time.sleep(15)

# function: routing
def routing():

	# global variables
	global NID, hostname, tcp_port
	global l1_hostname, l2_hostname, l3_hostname, l4_hostname
	global l1_tcp_port,l2_tcp_port, l3_tcp_port, l4_tcp_port	
	global l1_NID, l2_NID, l3_NID, l4_NID
	global l1_flag, l2_flag, l3_flag, l4_flag
	global update_flag_1, update_flag_2


	addresses = [(l1_NID,l1_hostname,l1_tcp_port),(l2_NID,l2_hostname,l2_tcp_port),(l3_NID,l3_hostname,l3_tcp_port),(l4_NID,l4_hostname,l4_tcp_port)]

	# start loop
	while(1):

		# update routes in all neighbor nodes
		message = pickle.dumps('rte' + ' ' + str(NID) + ' ' + str(routes))

		# iterate through address list
		for address in addresses:
			if address[0] == 0:
				pass

			else:

				# send route to neighbors
				try:
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)				
					sock.connect((address[1], address[2]))
					sock.sendall(message)
					sock.close()

				except:
					continue					

		# send this information every 30 seconds
		time.sleep(30)

# print status
def PrintStatus():

	# global variables
	global node, NID, hostname, udp_port, tcp_port

	os.system('clear')
	print("NID: " + str(NID))
	if l1_NID != 0:
		print("Link up to node " + str(l1_NID) + ':', (node.GetUpFlagL1()))
	if l2_NID != 0:
		print("Link up to node " + str(l2_NID) + ':', (node.GetUpFlagL2()))
	if l3_NID != 0:
		print("Link up to node " + str(l3_NID) + ':', (node.GetUpFlagL3()))
	if l4_NID != 0:
		print("Link up to node " + str(l4_NID) + ':', (node.GetUpFlagL4()))		
	print("Routes from " + str(NID) + ": ", routes)
	os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

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

		#print menu options
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
			sendto(int(dest_node), 15, message)
			os.system("""bash -c 'read -s -n 1 -p "Press any key to continue..."'""")

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