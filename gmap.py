import pydot
from collections import defaultdict
import subprocess
import sys
import os

def dot_to_scotch_newstyle(dot_path, grf_output_path):
    graphs = pydot.graph_from_dot_file(dot_path)
    graph = graphs[0]

    nodes = graph.get_nodes()
    node_id_map = {}
    node_weights = []
    id_counter = 0

    for node in nodes:
        name = node.get_name().strip('"')
        if name == 'node':
            continue
        node_id_map[name] = id_counter
        node_weights.append(int(node.get_attributes().get("cost", "1")))
        id_counter += 1

    edges = graph.get_edges()
    adjacency = defaultdict(set)
    edge_weights = {}

    for edge in edges:
        src = edge.get_source().strip('"')
        dst = edge.get_destination().strip('"')
        src_id = node_id_map[src]
        dst_id = node_id_map[dst]
        weight = int(edge.get_attributes().get("cost", "1"))

        adjacency[src_id].add((dst_id, weight))
        adjacency[dst_id].add((src_id, weight))
        edge_weights[frozenset((src_id, dst_id))] = weight

    num_vertices = len(node_weights)
    num_arcs = len(edge_weights) * 2

    lines = ["0"]
    lines.append(f"{num_vertices} {num_arcs}")
    lines.append("0 011")

    for vid in range(num_vertices):
        neighbors = sorted(adjacency[vid], key=lambda x: x[0])
        degree = len(neighbors)
        line = [str(node_weights[vid]), str(degree)]
        for neighbor_id, edge_weight in neighbors:
            line.append(f"{edge_weight} {neighbor_id}")
        lines.append(" ".join(line))

    os.makedirs(os.path.dirname(grf_output_path), exist_ok=True)
    with open(grf_output_path, "w") as f:
        f.write("\n".join(lines))
    print(f"✅ Converted to SCOTCH new-style .grf: {grf_output_path}")
    return num_vertices, node_id_map

def read_map_file(map_file_path):
    partition_map = {}
    with open(map_file_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 2:
            try:
                node_id = int(parts[0])
                part_id = int(parts[1])
                partition_map[node_id] = part_id
            except ValueError:
                continue
    return partition_map

def write_colored_dot(dot_path, partition_map, id_to_node, output_dot_path):
    graphs = pydot.graph_from_dot_file(dot_path)
    graph = graphs[0]

    color_palette = [
        "lightblue", "lightgreen", "lightcoral", "khaki", "plum",
        "lightsalmon", "gold", "lightgrey", "aquamarine", "thistle",
        "orange", "cyan", "salmon", "palegreen", "lavender"
    ]

    for node_id, part in partition_map.items():
        if node_id in id_to_node:
            node_name = id_to_node[node_id]
            matches = graph.get_node(f'"{node_name}"') or graph.get_node(node_name)
            if matches:
                node = matches[0]
                node.set("style", "filled")
                node.set("fillcolor", color_palette[part % len(color_palette)])

    os.makedirs(os.path.dirname(output_dot_path), exist_ok=True)
    graph.write_raw(output_dot_path)
    print(f"🎨 Colored DOT file written to: {output_dot_path}")

def run_gmap(grf_path, arch_path, map_output_path):
    try:
        result = subprocess.run(
            ["gmap", "-cbr", "-vm", grf_path, arch_path, map_output_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"✅ Ran gmap and saved map to: {map_output_path}")
        print("📤 gmap output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("❌ gmap failed:")
        print(e.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python gmap.py input.dot")
        sys.exit(1)

    dot_path = sys.argv[1]
    base_name = os.path.splitext(os.path.basename(dot_path))[0]

    grf_path = f"scotch/{base_name}.grf"
    map_output_path = f"scotch/{base_name}.map"
    arch_path = "hardware.arch"
    output_dot_path = f"dot_output/{base_name}.scotch.dot"

    num_vertices, node_id_map = dot_to_scotch_newstyle(dot_path, grf_path)
    run_gmap(grf_path, arch_path, map_output_path)
    partition_map = read_map_file(map_output_path)
    id_to_node = {v: k for k, v in node_id_map.items()}
    write_colored_dot(dot_path, partition_map, id_to_node, output_dot_path)
