This is a UDP socket client/server node that will communicate with it's neighbors to see if they are alive or not. Each
node will accept between 0-4 connections, and a network of any size can be built. The initial network topology is determined
by the itc.txt file. Currently, a node will only forward a message to the first link in it's list of neighbor links. The idea
is to use this for a project wherein students will implement a routing algorithm that will forward traffic through the network.
Once built, nodes can be taken off line to see if the routing algorithm is actually working properly.

Three options are available by GUI; status, send, quit.
status: shows the current status of the node, including name, address, topology, neighbors
send:   once running, the node will attempt to send a text message to another node in the network. This will require a routing
        algorithm be implemented by the student
quit:   this terminates the program.

To use, clone the 'Sockets' repo to a local file system. Open one terminal for each node in the network (they are all 'localhost'
at present, but IP addresses can be changed and this will actually run on the Internet or a live network). Enter the following
at the command line:

python program-name node-name topology file

for example:

python network_node.py 1 itc3.txt

The node name for each node must be unique, i.e. 1, 2, 3,......9, 10.
