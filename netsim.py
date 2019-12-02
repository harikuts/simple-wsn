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
nodeLookup[model.SINK] = nc.SensorNode(model.SINK, model.EDGE_DICT, model.SINK_BUFFER_SIZE)
for node in model.NODE_LIST:
    nodeLookup[node] = nc.SensorNode(node, model.EDGE_DICT, model.NODE_BUFFER_SIZE)

# Build neighbors and edges
for node in model.NODE_LIST:
    nodeLookup[node].add_neighbors(model.EDGE_DICT, nodeLookup)

for step in range(model.STEPS):
    nc.debug(DEBUG, "~~~ STEP %08d ~~~" % (step))
    for node in model.NODE_LIST:
        nodeLookup[node].transmit()
        messageCounter = maybe_send_message(node, messageCounter)
    for node in model.NODE_LIST:
        nodeLookup[node].update_node()
    nc.debug(DEBUG, "Successful messages: %d / %d" % (len(nodeLookup[model.SINK].rxBuffer), messageCounter))