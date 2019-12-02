#!/usr/bin/env

# NODE_LIST = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "S"]
NODE_LIST = ["A", "C", "D"]
SINK = "SINK"

EDGE_DICT = {}
EDGE_DICT["A"] = [("SINK", 1.00), ("C", 0.75), ("D", 0.72)]
EDGE_DICT["C"] = [("A", 0.75),]
EDGE_DICT["D"] = [("A", 0.72)]
EDGE_DICT["SINK"] = []

SINK_BUFFER_SIZE = 2048
NODE_BUFFER_SIZE = 8

MESSAGE_SEND_RATE = float(0.80 / len(NODE_LIST))
STEPS = 50