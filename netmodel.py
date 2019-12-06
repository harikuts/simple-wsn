#!/usr/bin/env

# NODE_LIST = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "S"]
NODE_LIST = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
NODE_RELIABILITY = {}
NODE_RELIABILITY["A"] = 0.91
NODE_RELIABILITY["B"] = 0.63
NODE_RELIABILITY["C"] = 0.66
NODE_RELIABILITY["D"] = 0.54
NODE_RELIABILITY["E"] = 0.71
NODE_RELIABILITY["F"] = 0.80
NODE_RELIABILITY["G"] = 0.71
NODE_RELIABILITY["H"] = 0.92
NODE_RELIABILITY["I"] = 0.81

SINK = "SINK"
SINK_RELIABILITY = 1.0

EDGE_DICT = {}
EDGE_DICT["A"] = [(SINK, 20), ("B", 8), ("C", 32), ("D", 17), ("E", 17), ("F", 17)]
EDGE_DICT["B"] = [(SINK, 8), ("A", 17), ("G", 39), ("C", 12)]
EDGE_DICT["C"] = [(SINK, 48), ("A", 32), ("B", 12), ("D", 8), ("G", 18), ("H", 28)]
EDGE_DICT["D"] = [(SINK, 58), ("A", 17), ("C", 8), ("E", 17), ("H", 30), ("I", 24)]
EDGE_DICT["E"] = [("A", 17), ("D", 17), ("F", 4), ("H", 38), ("I", 12)]
EDGE_DICT["F"] = [("A", 17), ("E", 4), ("I", 12)]
EDGE_DICT["G"] = [("B", 39), ("C", 18), ("H", 12)]
EDGE_DICT["H"] = [("C", 28), ("D", 30), ("E", 38), ("G", 12), ("I", 12)]
EDGE_DICT["I"] = [("D", 24), ("E", 12), ("F", 12), ("H", 12)]
EDGE_DICT["SINK"] = []

SINK_BUFFER_SIZE = 2048
NODE_BUFFER_SIZE = 4

MESSAGE_SEND_RATE = float(2.0 / len(NODE_LIST))
STEPS = 2000
COOL_DOWN = 200