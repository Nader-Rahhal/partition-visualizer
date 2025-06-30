import argparse
import pydot
from collections import defaultdict
import json

parser = argparse.ArgumentParser(description="Convert DOT graph to METIS .graph format")
parser.add_argument("dot_input", help="Path to input DOT file")
parser.add_argument("graph_output", help="Path to output METIS .graph file")
args = parser.parse_args()

graph, = pydot.graph_from_dot_file(args.dot_input)

node_weights = {}
adj = defaultdict(list)
node_to_id = {}
id_to_node = {}
next_id = 1

def get_node_id(name):
    global next_id
    if name not in node_to_id:
        node_to_id[name] = next_id
        id_to_node[next_id] = name
        next_id += 1
    return node_to_id[name]

for node in graph.get_nodes():
    name = node.get_name().strip('"')
    node_id = get_node_id(name)
    weight = node.get("cost")
    node_weights[node_id] = weight if weight is not None else "1"

for edge in graph.get_edges():
    src = get_node_id(edge.get_source().strip('"'))
    dst = get_node_id(edge.get_destination().strip('"'))
    weight = int(edge.get("cost") or 1)
    adj[src].append((dst, weight))
    adj[dst].append((src, weight))

for node_id in range(1, next_id):
    if node_id not in node_weights:
        node_weights[node_id] = "1"

with open(args.graph_output, "w") as f:
    num_nodes = next_id - 1
    num_edges = sum(len(neighbors) for neighbors in adj.values()) // 2
    f.write(f"{num_nodes} {num_edges} 11\n")
    for node_id in range(1, next_id):
        weight = node_weights[node_id]
        neighbors = adj.get(node_id, [])
        line = [str(weight)]
        for neighbor_id, edge_weight in neighbors:
            line.append(str(neighbor_id))
            line.append(str(edge_weight))
        f.write(" ".join(line) + "\n")

print(f"[✓] METIS graph file written to {args.graph_output}")

mapping_path = args.graph_output + ".mapping.json"
with open(mapping_path, "w") as mapfile:
    json.dump(id_to_node, mapfile)
print(f"[✓] Mapping file written to {mapping_path}")
