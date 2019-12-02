#!/usr/bin/env

import pdb

import netmodel as model
import netcomponents as nc
import random

DEBUG = 1

nodeLookup = {}
messageCounter = 0

# Message generator
def maybe_send_message(node, messageCounter):
    if random.random() < model.MESSAGE_SEND_RATE:
        message = "%08d" % (messageCounter)
        nc.debug(DEBUG, "Sending message [%s] from %s" % (message, node))
        nodeLookup[node].send(message, model.SINK)
        messageCounter += 1
    return messageCounter


# Construct each node and the sink
nodeLookup[model.SINK] = nc.SensorNode(model.SINK, model.EDGE_DICT, model.SINK_BUFFER_SIZE, model.SINK_RELIABILITY)
for node in model.NODE_LIST:
    nodeLookup[node] = nc.SensorNode(node, model.EDGE_DICT, model.NODE_BUFFER_SIZE, model.NODE_RELIABILITY[node])

# Build neighbors and edges
for node in model.NODE_LIST:
    nodeLookup[node].add_neighbors(model.EDGE_DICT, nodeLookup)

# Compute shortest distances
nodeDistances = []
for node in model.NODE_LIST:
    nodeLookup[node].get_shortest_dist(model.SINK, model.EDGE_DICT)
    nodeDistances.append(nodeLookup[node].distance)
# Set max distances
maxDistance = max(nodeDistances)
for node in model.NODE_LIST:
    nodeLookup[node].maxDistance = maxDistance
    nc.debug(DEBUG, nodeLookup[node].generate_stats(distanceWanted=True))
nc.debug(DEBUG, "Max distance: %d" % (maxDistance))

pdb.set_trace()

# Run simulation
for step in range(model.STEPS):
    nc.debug(DEBUG, "~~~ STEP %08d ~~~" % (step))
    for node in model.NODE_LIST:
        nodeLookup[node].transmit()
        messageCounter = maybe_send_message(node, messageCounter)
    for node in model.NODE_LIST:
        nodeLookup[node].update_node()
    nc.debug(DEBUG, "Successful messages: %d / %d" % (len(nodeLookup[model.SINK].rxBuffer), messageCounter))