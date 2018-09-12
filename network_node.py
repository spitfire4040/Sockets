# header files
import socket
import sys
import thread
import SocketServer
import os
import time
import random

# set global variables
hostname = ' '
port = 0
l1_hostname = ' '
l1_port = ' '
l2_hostname = ' '
l2_port = ' '
l3_hostname = ' '
l3_port = ' '
l4_hostname = ' '
l4_port = ' '
l1_flag = False
l2_flag = False
l3_flag = False
l4_flag = False
t1_flag = False
t2_flag = False
t3_flag = False
t4_flag = False
mynode = None

# create node object variable
node = None

# function: InitializeTopology
def InitializeTopology (nid, itc):

	# global variables
	global mynode

	# initialize node object
	node = Node(nid)
	mynode = node

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
		ports.append(temp[2])

	# use list to populate LinkTable and PortTable
	for entry in list:
		temp = entry.split(' ')
		node.Set_link_table(int(temp[0]), (int(temp[3]), int(temp[4]), int(temp[5]), int(temp[6])))
		node.Set_address_data_table(temp[0], temp[1], temp[2])

		# set parameters for for this node
		if node.GetNID() == temp[0]:
			node.SetHostName(temp[1])
			node.SetPort(temp[2])

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
		#pass

	# print status
	def PrintStatus(self):

		os.system('clear')
		print "Status of this node"
		print "-------------------"
		print "NID: ", (self.nid)
		print "HostName: ", (self.host_name)
		print "UDP Port: ", (self.udp_port)
		print "Links: ", self.links
		print "Link Table: ", (self.link_table)
		print "Link 1 up: ", (self.upL1)
		print "Link 2 up: ", (self.upL2)
		print "Link 3 up: ", (self.upL3)
		print "Link 4 up: ", (self.upL4)
		print "Address Data Table: ", (self.address_data_table)
		print "-------------------"
		raw_input("press 'enter' to continue....")

# Class: MyUDPHandler
class MyUDPHandler(SocketServer.BaseRequestHandler):

	# interrupt handler for incoming messages
	def handle(self):

		# global variables
		global mynode, l1_port, l2_port, l3_port, l4_port, l1_flag, l2_flag, l3_flag, l4_flag

		# open file for routing table
		rt = open("routing_table.txt", "w")

		# parse received data
		data = self.request[0].strip()

		# set message and split
		message = data
		message = message.split()

		# look for 'hello' message (this is for the 'is-alive' functionality)
		if message[0] == "hhhhh":

			# set link flags
			if message[1] == l1_port:
				l1_flag = True

			if message[1] == l2_port:
				l2_flag = True

			if message[1] == l3_port:
				l3_flag = True

			if message[1] == l4_port:
				l4_flag = True          

		# not hello, forward to appropriate neighbor
		else:
			print message

		rt.close()

# Function: sendto()
def sendto(node, dest_nid, message):

	# global variables
	global mynode
	link_list = []

	# get node NID's (this node and the node that sent the message)
	this_nid = mynode.GetNID() # get the NID of the current node (this node)
	current_nid = node.GetNID() # get the NID of the node we were passed in this function


	# send message to the first neighbor of this node
	# NOTE: this is where you will need to build the logic for forwarding messages from host to host and implement
	#       your routing algorithm. At present, it simply sends the message to the current host's first link, but it should
	#       route traffic through the matrix to the appropriate recipient.


	# get link table and find links for this node
	links = node.Get_link_table()
	for link in links:
		if int(link) == int(node.GetNID()): # find my own node ID
			this_node = links[link]
			n1 = this_node[0] # neighbor 1
			n2 = this_node[1] # neighbor 2
			n3 = this_node[2] # neighbor 3
			n4 = this_node[3] # neighbor 4

	# get links for this node
	links = node.GetLinks()
	link1 = links[0]
	link2 = links[1]
	link3 = links[2]
	link4 = links[3]
 
	# set recipient hostname and port for socket
	dest_hostname = link1[1]
	dest_port = link1[2]

	# create udp socket and send
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto(message, (dest_hostname, int(dest_port)))

# function: start listener
def start_listener(node):

	# global variables
	global mynode, hostname, port, nid, l1_hostname, l1_port, l2_hostname, l2_port

	mynode = node

	# check links for node attributes
	links = node.GetLinks()
	link1 = links[0]
	link2 = links[1]
	link3 = links[2]
	link4 = links[3]

	l1_hostname = link1[1]
	l1_port = link1[2]

	l2_hostname = link2[1]
	l2_port = link2[2]

	l3_hostname = link3[1]
	l3_port = link3[2]

	l4_hostname = link4[1]
	l4_port = link4[2]  

	hostname = node.GetHostName()
	nid = node.GetNID()
	port = node.GetPort()

	# slight pause to let things catch up
	time.sleep(2)

	# start threads for listener
	thread.start_new_thread(receiver, ())
	thread.start_new_thread(hello, ())
	thread.start_new_thread(timer, (node,))


# function: receiver (listener)
def receiver():

	# global variables
	global hostname, port
	# set socket for listener
	try:
		server = SocketServer.UDPServer((hostname, int(port)), MyUDPHandler)
		server.serve_forever()

	# report error if fail
	except:
		print "failed to start listener"

# function: hello (alive)
def hello():

	# global variables
	global hostname, port, l1_hostname, l1_port, l2_hostname, l2_port, l3_hostname, l3_port, l4_hostname, l4_port

	# eternal loop
	while (1):

		try:
			# open socket and send to neighbor 1
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			sock.sendto("hhhhh" + ' ' + port, (l1_hostname, int(l1_port)))
			time.sleep(1)
		except:
			pass

		try:
			# open socket and send to neighbor 2
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			sock.sendto("hhhhh" + ' ' + port, (l2_hostname, int(l2_port)))
			time.sleep(1)
		except:
			pass

		try:
			# open socket and send to neighbor 3
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			sock.sendto("hhhhh" + ' ' + port, (l3_hostname, int(l3_port)))
			time.sleep(1)
		except:
			pass

		try:
			# open socket and send to neighbor 4
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			sock.sendto("hhhhh" + ' ' + port, (l4_hostname, int(l4_port)))
			time.sleep(1)
		except:
			pass           

# function: timer (for hello)
def timer(node):

	# global variables 
	global l1_flag, l2_flag, l3_flag, l4_flag

	# eternal loop
	while (1):

		# first wait 10 seconds, then set flags to false (reset)
		for x in range(10):
		  time.sleep(1)
		l1_flag = False
		l2_flag = False
		l3_flag = False
		l4_flag = False

		# now check for true for 5 second period
		for x in range(2):
			time.sleep(1)

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

# main function
def main(argv):

	# global variables
	global node

	# set initial value for loop
	run = 1

	# check for command line arguments
	if len(sys.argv) != 3:
		print "Usage: <program_file><nid><itc.txt>"
		exit(1)

	# initialize node object
	node = InitializeTopology(sys.argv[1], sys.argv[2])

	# start UDP listener
	start_listener(node)

	# loop
	while(run):

		# print menu options
		os.system('clear')
		print "Enter 'status' to check node status"
		print "Enter 'send' to message another node"
		print "Enter 'quit' to end program"

		# set selection value from user
		selection = raw_input("Enter Selection: ")

		# selection: status
		if selection == 'status':
			node.PrintStatus()

		# selection: send
		elif(selection == 'send'):
			os.system('clear')
			dest_node = raw_input("enter the node you want to message: ")
			message = raw_input("enter the message you want to send: ")
			sendto(node, dest_node, message)
			raw_input("press 'enter' to continue...")

		# selection: quit
		elif(selection == 'quit'):
			run = 0
			os.system('clear')

		else:

			# default for bad input
			os.system('clear')
			print 'selection not valid, please try again...'
			time.sleep(1.5)
			continue

# initiate program
if __name__ == "__main__":
	main(sys.argv)