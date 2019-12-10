simple-wsn
==============
A simple WSN simulator in Python for routing, power consumption, and congestion purposes. Used to test for routing protocols and (one day) sensor node characteristics.

Configuration
--------------
The network configuration is done in **netmodel.py**. The user (as of now) must provide a network bi-directional graph with (1) a *list of nodes* with corresponding *inherent unreliability values*, (2) *connected edges* between nodes and their corresponding *distances along edges*, and (3) *simulation run time* (where nodes are actively sending messages) and *cool down time* (where nodes cease sending messages and messages currently in the network continue to reach the sink), both of which are in units of steps. The attached model can be used as an example.

Run
--------------
To run, configure **netmodel.py**. Then simply run:
  python netsim.py

Files
===============
The simulator requires the configuration script **netmodel.py**, the network components code **netcomponents.py**, and the simulation executable **netsim.py**.

netmodel.py
--------------
This file contains the network configuration model. The user can use this example to make their own network configuration file, but it must be included in the **netsim.py** file (to do: take this model as an argument). See *Configuration* for more details.

netcomponents.py
--------------
This file holds the actual components of network operations. This includes the Message and SensorNode objects. This includes standard node mechanisms (RX/TX buffer mechanisms, send and receive functions, power depletion, and congestion reporting functions. This file also holds the routing protocol through the *_get_next_hop* function. For now this routing protocol is set to be Q-learning and MDP implementations for the sake of the project this was originally written for. Future implementations will create an extendable framework to plug-and-play custom protocols.

netsim.py
--------------
This file acts as the executable file. It includes the other two files. It first initializes the network simulation and goes through a discovery phase, then begins the simulation. Reporting is done so at the end.
