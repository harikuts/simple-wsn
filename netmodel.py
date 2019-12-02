#!/usr/bin/env

# NODE_LIST = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "S"]
NODE_LIST = ["A", "B", "C", "D"]
NODE_RELIABILITY = {}
NODE_RELIABILITY["A"] = 0.84
NODE_RELIABILITY["B"] = 0.68
NODE_RELIABILITY["C"] = 0.72
NODE_RELIABILITY["D"] = 0.67

SINK = "SINK"
SINK_RELIABILITY = 1.0

EDGE_DICT = {}
EDGE_DICT["A"] = [(SINK, 18), ("C", 21), ("D", 17)]
EDGE_DICT["B"] = [(SINK, 100), ("D", 24)]
EDGE_DICT["C"] = [("A", 21), ("D", 5)]
EDGE_DICT["D"] = [("A", 17), ("B", 24), ("C", 5)]
EDGE_DICT["SINK"] = []

SINK_BUFFER_SIZE = 2048
NODE_BUFFER_SIZE = 8

MESSAGE_SEND_RATE = float(0.80 / len(NODE_LIST))
STEPS = 10