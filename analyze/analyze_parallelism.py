#!/usr/bin/env python3
import sys
import networkx as nx
import pydot
from networkx.drawing.nx_pydot import from_pydot

if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} <input.dot>")
    sys.exit(1)

dot_path = sys.argv[1]

# === Load DOT ===
try:
    pydot_graph = pydot.graph_from_dot_file(dot_path)[0]
    G = from_pydot(pydot_graph)
except Exception as e:
    print(f"[!] Failed to parse DOT file: {e}")
    sys.exit(1)

if not isinstance(G, nx.DiGraph):
    G = G.to_directed()

G.remove_edges_from(nx.selfloop_edges(G))

if not nx.is_directed_acyclic_graph(G):
    print("[!] The input graph is not a DAG.")
    sys.exit(1)

# === Node Weights ===
node_weights = {}
for node in G.nodes:
    cost_attr = G.nodes[node].get("cost")
    try:
        node_weights[node] = int(cost_attr) if cost_attr else 1
    except ValueError:
        node_weights[node] = 1

for node, weight in node_weights.items():
    G.nodes[node]["weight"] = weight

# === Metrics ===
work = sum(node_weights.values())

# Compute critical path using node weights (ignore edge weights)
try:
    def weight_func(u, v, d):
        return node_weights[u]  # weight of source node

    critical_path = nx.dag_longest_path(G, weight=weight_func)
    span = sum(node_weights[n] for n in critical_path)
except Exception:
    critical_path = []
    span = 1

stages = list(nx.topological_generations(G))
max_parallel = max(len(stage) for stage in stages)

# === Output ===
print(f"Total nodes: {len(G.nodes)}")
print(f"Work (sum of node costs): {work}")
print(f"Span (critical path cost): {span}")
print(f"Max parallel width (stage size): {max_parallel}")
print(f"Parallelism Ratio: {work / span}")
for P in [1, 2, 4, 8, 16, 32, 64]:
    slackness = work / (P * span)
    print(f"Slackness @ P={P:>2}: {slackness:.2f}")

print()

print("Critical path:")
print("  -> ".join(critical_path))
print()

print("Parallel Stages (with cost):")
for i, stage in enumerate(stages):
    total_stage_cost = sum(node_weights.get(node, 1) for node in stage)
    print(f"  Stage {i}: {len(stage)} nodes, total cost = {total_stage_cost}")
