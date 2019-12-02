#!/usr/bin/env
import random
import pdb

DEBUG = 1
POWER_DEPLETE = 0.01

W_D = 0.25
W_L = 0.25
W_C = 0.25
W_P = 0.25
Q_DEPTH = 2

# Debug command for development
def debug(flag, message):
    if flag:
        print (message)

# Basic message class
class Message:
    DELIVERED = 0
    SUCCESS = 1
    FAIL = 2
    def __init__(self, src, dest, data):
        self.src = src
        self.dest = dest
        self.data = data
        self.path = [src]

# Basic neighbor class
class Connection:
    def __init__(self, node, reliability):
        self.node = node
        self.reliability = reliability

# Basic sensor node class
class SensorNode:
    def __init__(self, name, adjDict, bufferSize, power=1, powerDeplete=POWER_DEPLETE):
        self.name = name
        # Neighbor initialization from adjacency list
        self.neighbors = []
        # Calculate distance using Djikstra's for shortest number of hops
        self.distance = 0
        self.maxDistance = 1
        # Assign power
        self.power = power
        self.powerDeplete = powerDeplete
        # Set up buffer
        self.rxBuffer = []
        self.txBuffer = []
        self.maxBufferSize = bufferSize
        self.congestion = 0

    # Report stats. Returns string.
    def generate_stats(self):
        return ("Node %s - PWR: %f | CON: %f | RX: %d | TX: %d" \
            % (self.name, self.power, self.congestion, len(self.rxBuffer), len(self.txBuffer)))

    # Node update per step (NOT COMPLETE)
    def update_node(self):
        UP_DEBUG = 1
        # Update congestion information
        self.congestion = float(len(self.rxBuffer)) / self.maxBufferSize
        # Report stats first
        debug(UP_DEBUG, self.generate_stats())
        # If node has no power, it is dead
        if self.power <= 0:
            debug(UP_DEBUG, "UP: Node %s is dead. Cannot update." % (self.name))
            return
        debug(UP_DEBUG, "UP: Updating %s..." % (self.name))
        # Deplete power
        self.consume_power()

        # Process buffers
        if len(self.rxBuffer):
            m = self.rxBuffer.pop()
            # Check if message has reached destination
            if self.name == m.dest:
                debug(UP_DEBUG, "UP: Destination reached.")
                pass
            # Move from rx to tx
            else:
                if len(self.txBuffer) < self.maxBufferSize:
                    debug(UP_DEBUG, "UP: Moving message from RX to TX.")
                    self.txBuffer.append(m)
                    self.consume_power()
                else:
                    debug(UP_DEBUG, "UP: TX buffer is full.")
            m.path.append(self.name)
    
    # Message transit update
    def transmit(self):
        TX_DEBUG = 1
        # If node has no power, it is dead
        if self.power <= 0:
            debug(TX_DEBUG, "UP: Node %s is dead. Cannot transmit." % (self.name))
            return
        debug(TX_DEBUG, "TX: Checking %s's TX..." % (self.name))
        if len(self.txBuffer):
            debug(TX_DEBUG, "TX: \tTransmitting from %s..." % (self.name))
            m = self.txBuffer.pop()
            #pdb.set_trace()
            nextHop = self._get_next_hop(m.path[-2] if len(m.path) >= 2 else m.path[-1]) 
            if nextHop is not None:
                if random.random() <= nextHop.reliability:
                    debug(TX_DEBUG, "TX: \t\tLink (" + self.name + "->" + nextHop.node.name + ") SUCCESS.")
                    transmitSuccess = nextHop.node.receive(m)
                else:
                    debug(TX_DEBUG, "TX: \t\tLink (" + self.name + "->" + nextHop.node.name + ") FAILED.")
                    transmitSuccess = False
                debug(TX_DEBUG, "TX: \t\tMessage ('" + m.data + "') from " + self.name + " to " + nextHop.node.name + " : " + str(transmitSuccess))
                debug(TX_DEBUG, "TX: \t\tPath: " + str(m.path))
                # Deplete power, whether or not link is reached
                self.consume_power()
            else:
                debug(TX_DEBUG, "TX: \t\tNext-hop not available.")
    
    # Store into message buffer
    def receive(self, message):
        RX_DEBUG = 1
        # If node has no power, it is dead
        if self.power <= 0:
            debug(RX_DEBUG, "UP: Node %s is dead. Cannot receive." % (self.name))
            return False
        # If the buffer isn't full, store the message
        if len(self.rxBuffer) < self.maxBufferSize:
            self.rxBuffer.append(message)
            # debug(RX_DEBUG, "\tRX: Path after: %s" % (str(self.rxBuffer[-1].path)))
            # Deplete power
            self.consume_power()
            return True
        # If the buffer is full, return error
        else:
            return False

    # Send a message originating at this node
    def send(self, data, dest):
        m = Message(self.name, dest, data)
        if len(self.txBuffer) < self.maxBufferSize:
            self.txBuffer.append(m)
            # Deplete power
            self.consume_power()
    
    # Get congestion value (NOT COMPLETE)
    def get_congestion(self):
         return (float(len(self.rxBuffer)) + float(len(self.rxBuffer))) \
              / (2 * self.maxBufferSize)

    # Power depletion function
    def consume_power(self):
        self.power = max(0, self.power - self.powerDeplete)

    # Construct neighbors list
    def add_neighbors(self, adjDict, nodeLookup):
        self.nodeLookup = nodeLookup
        # For each node in this node's entry in the adjacency list
        for n in adjDict[self.name]:
            # Append a neighbor object
            self.neighbors.append(Connection(self.nodeLookup[n[0]], n[1]))

    # Get distance to sink
    def _get_shortest_hops(self):
        pass

    # Get next hop (DUMMY FUNCTION for now)
    def _get_next_hop(self, prevHop):
        NH_DEBUG = 0
        debug(NH_DEBUG, "NH: Getting next hop for %s" % (self.name))
        # Create list of viable neighbors
        viableNeighbors = []
        debug(NH_DEBUG, "NH: \tPrevious hop: %s" % (prevHop))
        for neighbor in self.neighbors:
            debug(NH_DEBUG, "NH: \t\tChecking %s" % (neighbor.node.name))
            if (neighbor.node.name is not prevHop):
                viableNeighbors.append(neighbor)
        debug(NH_DEBUG, "NH: \tViable neighbors: %s" % (str([n.node.name for n in viableNeighbors])))
        # Return first neighbor
        if len(viableNeighbors):
            return(viableNeighbors[0])
        else:
            return None
    
    # Reinforcement learning
    def generate_Q_value(self):
        # r = W_D * (1 - float(self.distance) / self.maxDistance) + \
        #     W_L * (1)
        pass