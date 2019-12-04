#!/usr/bin/env
import random
import pdb

DEBUG = 0
POWER_DEPLETE = 0.0015

INFINITY = 4096

W_D = 0.3
W_L = 0.3
W_C = 0.1
W_P = 0.3
Q_DEPTH = 2
DISCOUNT_RATE = 0.5

ALPHA_RATE = 0.9
BETA_RATE = 0.5
HISTORY_WINDOW = 4
MAX_LEARNED_REWARD = sum(ALPHA_RATE**i for i in [1] * HISTORY_WINDOW)

# Debug command for development
def debug(flag, message):
    if flag:
        print (message)

# Basic message class
class Message:
    DELIVERED = 0
    SUCCESS = 1
    FAIL = 2
    def __init__(self, src, dest, data, ttl):
        self.src = src
        self.dest = dest
        self.data = data
        self.path = [src]
        self.ttl = ttl

# Basic neighbor class
class Connection:
    def __init__(self, thisNode, thatNode, distance):
        self.node = thatNode
        self.reliability = (thisNode.reliability + thatNode.reliability) / 2
        self.distance = distance

# Basic sensor node class
class SensorNode:
    def __init__(self, name, adjDict, bufferSize, reliability, power=1, powerDeplete=POWER_DEPLETE):
        self.name = name
        self.sinkName = "SINK"
        # Neighbor initialization from adjacency list
        self.neighbors = []
        # Calculate distance using Djikstra's for shortest number of hops
        self.distance = INFINITY
        self.maxDistance = 1
        # Assign power
        self.power = power
        self.powerDeplete = powerDeplete
        # Assign reliability
        self.reliability = reliability
        # Set up buffer
        self.rxBuffer = []
        self.txBuffer = []
        self.maxBufferSize = bufferSize
        self.congestion = 0
        # Maintain learned reward history
        self.histories = {}
        self.history = [1] * HISTORY_WINDOW
        # Set up Q-value
        self.Q = 2 if self.name == self.sinkName else 0

    # Report stats. Returns string.
    def generate_stats(self, distanceWanted=False):
        stats = ("Node %s - PWR: %f | CON: %f | RX: %d | TX: %d | Q: %f" \
            % (self.name, self.power, self.congestion, \
                len(self.rxBuffer), len(self.txBuffer), self.Q))
        if distanceWanted:
            stats = stats + " | DST: %d" % (self.distance)
        return stats

    # Node update per step (NOT COMPLETE)
    def update_node(self):
        UP_DEBUG = 1
        # If node has no power, it is dead
        if self.power <= 0:
            debug(UP_DEBUG, "UP: Node %s is dead. Cannot update." % (self.name))
            return
        debug(UP_DEBUG, "UP: Updating %s..." % (self.name))
        # Update congestion information
        self.congestion = self.get_congestion()
        # Deplete power
        self.consume_power()
        # Generate Q value
        self.Q = self.generate_Q_value_plus()
        # Report stats for everything
        debug(UP_DEBUG, self.generate_stats())
        for n in self.neighbors:
            debug(UP_DEBUG, "\t%s :: %s" % (n.node.name, str(self.histories[n.node.name])))

        # Process buffers
        if len(self.rxBuffer):
            m = self.rxBuffer.pop(0)
            # print(m.data, " ", m.ttl)
            if m.ttl <= 0:
                print("\nMESSAGE DIED LOL\n")
                return
            # Check if message has reached destination
            if self.name == m.dest:
                debug(UP_DEBUG, "UP: Destination reached.")
                # print(m.data, " REACHED ", m.ttl)
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
            debug(TX_DEBUG, "TX: Node %s is dead. Cannot transmit." % (self.name))
            return
        # Check node's TX to see if there is a message to be sent
        debug(TX_DEBUG, "TX: Processing %s's TX..." % (self.name))
        if len(self.txBuffer):
            debug(TX_DEBUG, "TX: \tTransmitting from %s..." % (self.name))
            # Pop the message off the buffer
            m = self.txBuffer.pop(0)
            # Acquire the next hop, function returns a Connection object
            nextHop = self._get_next_hop(m.path[-2] if len(m.path) >= 2 else m.path[-1]) 
            if nextHop is not None:
                # Decrease ttl
                m.ttl = m.ttl - nextHop.distance
                debug(TX_DEBUG, "TX: \t\tLink (" + self.name + "->" + nextHop.node.name \
                     + ") with " + str(nextHop.reliability) + " reliability...")
                # Transmit message based on reliability (could be moved to another function at some point.)
                if random.random() <= nextHop.reliability:
                    debug(TX_DEBUG, "TX: \t\t\t...SUCCESS.")
                    transmitSuccess = nextHop.node.receive(m)
                    if transmitSuccess:
                        debug(TX_DEBUG, "TX: \t\tMessage sent.")
                    else:
                        debug(TX_DEBUG, "TX: \t\tMessage still failed (error on receiving end).")
                else:
                    debug(TX_DEBUG, "TX: \t\t\t...FAILED.")
                    transmitSuccess = False
                debug(TX_DEBUG, "TX: \tMessage from " + self.name + " to " + nextHop.node.name + " : " + str(transmitSuccess))
                # Record interaction for rewards
                self.record_reward(nextHop.node.name, transmitSuccess)
                # Deplete power, whether or not link is reached
                self.consume_power()
            else:
                debug(TX_DEBUG, "TX: \tNext-hop not available.")
    
    # Store into message buffer
    def receive(self, message):
        RX_DEBUG = 0
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
    def send(self, data, dest, ttl):
        m = Message(self.name, dest, data, ttl=ttl)
        if len(self.txBuffer) < self.maxBufferSize:
            self.txBuffer.append(m)
            # Deplete power
            self.consume_power()
    
    # Get congestion value (NOT COMPLETE)
    def get_congestion(self):
         return (float(len(self.rxBuffer)) + float(len(self.txBuffer))) \
              / (2 * self.maxBufferSize)

    # Power depletion function
    def consume_power(self):
        self.power = max(0, self.power - self.powerDeplete)

    # Record history
    def record_reward(self, nodeName, success):
        self.histories[nodeName].pop(0)
        self.histories[nodeName].append(1 if success is True else 0)
    
    # Get record
    def get_record(self, nodeName):
        past_rewards = []
        for i in range(len(self.histories[nodeName])):
            past_reward = ALPHA_RATE**i * self.histories[nodeName][-i]
            past_rewards.append(past_reward)
        learned_reward = sum(past_rewards) / MAX_LEARNED_REWARD
        return learned_reward

    # Construct neighbors list
    def add_neighbors(self, adjDict, nodeLookup):
        self.nodeLookup = nodeLookup
        # For each node in this node's entry in the adjacency list
        for n in adjDict[self.name]:
            # Append a neighbor object
            self.neighbors.append(Connection(self, self.nodeLookup[n[0]], n[1]))
            self.histories[n[0]] = [1] * HISTORY_WINDOW

    # Get distance to sink
    def get_shortest_dist(self, sinkName, adjDict, prevHop=[]):
        SD_DEBUG = 0
        debug(SD_DEBUG, "Getting shortest route for %s given %s..." % (self.name, str(prevHop)))
        # If sink is reached, return 0
        if self.name == sinkName:
            self.distance = 0
            return self.distance
        # Create list of viable neighbors
        viableNeighbors = []
        debug(SD_DEBUG, "%s\tAll neighbors: %s" % (self.name, str([n.node.name for n in self.neighbors])))
        debug(SD_DEBUG, "%s\t\tAll distances: %s" % (self.name, str([n.distance for n in self.neighbors])))
        for neighbor in self.neighbors:
            if (neighbor.node.name not in prevHop):
                viableNeighbors.append(neighbor)
        debug(SD_DEBUG, "%s\t\tViable neighbors: %s" % (self.name, str([n.node.name for n in viableNeighbors])))
        # If there's a dead end, return infinity
        if len(viableNeighbors) == 0:
            return INFINITY
        # Get possible distances
        possibleDists = []
        for n in viableNeighbors:
            distToNeighbor = n.distance
            debug(SD_DEBUG, "%s\tDist. to %s: %d" % (self.name, n.node.name, n.distance))
            possibleDists.append(distToNeighbor + \
                n.node.get_shortest_dist(sinkName, adjDict, prevHop=prevHop+[self.name]))
        debug(SD_DEBUG, "%s\tPossible dists. given %s: %s" % (self.name, str(prevHop), str(possibleDists)))
        # If we're back at the top level of recursion, assign the distance
        if len(prevHop) == 0:
            self.distance = min(possibleDists + [self.distance])
            debug(SD_DEBUG, "%s\t\tAssigning own dist. to sink: %d" % (self.name, self.distance))
            return self.distance
        # If we're still in the recursion, just return the min of possible distances
        return min(possibleDists)


    # Get next hop (DUMMY FUNCTION for now)
    def _get_next_hop(self, prevHop):
        NH_DEBUG = 1
        debug(NH_DEBUG, "NH: Getting next hop for %s" % (self.name))
        # Create list of viable neighbors
        viableNeighbors = []
        debug(NH_DEBUG, "NH: \tPrevious hop: %s" % (prevHop))
        for neighbor in self.neighbors:
            # debug(NH_DEBUG, "NH: \t\tChecking %s" % (neighbor.node.name))
            if (neighbor.node.name is not prevHop):
                viableNeighbors.append(neighbor)
        debug(NH_DEBUG, "NH: \tViable neighbors: %s" % (str([n.node.name for n in viableNeighbors])))
        # Return neighbor based on best inherent Q-value
        if len(viableNeighbors):
            # nextHopOptions = (sorted(viableNeighbors, key=(lambda x: x.node.Q)))
            nextHopOptions = (sorted(viableNeighbors, key=(lambda x: x.node.Q + self.get_record(x.node.name))))
            for pn in nextHopOptions:
                debug(NH_DEBUG, "NH:\t\t%s: %f %f" % (pn.node.name, pn.node.Q, self.get_record(pn.node.name)))
            nextHop = nextHopOptions[-1]
            debug(NH_DEBUG, "NH: \t\tNext hop: %s" % (nextHop.node.name))
            return nextHop
        else:
            return None
    
    # Reinforcement learning
    def generate_Q_value_naive(self, depthLevel=0):
        if self.name == self.sinkName:
            return 2
        r = W_D * (1 - float(self.distance) / self.maxDistance) + \
            W_L * (self.reliability) + \
            W_C * (1 - self.congestion) + \
            W_P * (self.power)
        if depthLevel < Q_DEPTH:
            return r + DISCOUNT_RATE * max([n.node.generate_Q_value_naive(depthLevel=depthLevel+1) for n in self.neighbors])
        else:
            return r
    
    def generate_Q_value_plus(self, depthLevel=0):
        if self.name == self.sinkName:
            return 2
        # Inherent perceived value
        v = W_D * (1 - float(self.distance) / self.maxDistance) + \
            W_L * (self.reliability) + \
            W_C * (1 - self.congestion) + \
            W_P * (self.power)
        if depthLevel < Q_DEPTH:
            expected_rewards = []
            for n in self.neighbors:
                # learned_reward = sum([ALPHA_RATE^i * self.histories[n.node.name].reverse()[i] for i in range(len(self.histories[n.node.name]))])
                learned_reward = self.get_record(n.node.name)
                neighbor_Q = n.node.generate_Q_value_plus(depthLevel=depthLevel+1)
                expected_rewards.append(learned_reward + neighbor_Q)
            return (1 - BETA_RATE) * v + BETA_RATE * max(expected_rewards)
        else:
            return v