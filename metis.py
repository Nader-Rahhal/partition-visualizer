import argparse
import subprocess
import os
import pydot
import json
from collections import defaultdict

parser = argparse.ArgumentParser(description="Partition a DOT file using METIS and color it")
parser.add_argument("dot_input", help="Input DOT file")
parser.add_argument("dot_output", help="Colored output DOT file")
parser.add_argument("num_parts", type=int, help="Number of partitions")
parser.add_argument("-v", "--view", action="store_true", help="View the output graph as PDF")
args = parser.parse_args()

graph_dir = "graph"
os.makedirs(graph_dir, exist_ok=True)

base_graph_file = os.path.splitext(os.path.basename(args.dot_input))[0]
graph_file = os.path.join(graph_dir, base_graph_file + ".graph")
part_file = graph_file + f".part.{args.num_parts}"
mapping_path = graph_file + ".mapping.json"

subprocess.run([
    "python3", "dot2graph.py",
    args.dot_input,
    graph_file
], check=True)

subprocess.run([
    "gpmetis",
    "-contig",
    "-objtype=cut",
    "-ptype=kway",
    graph_file,
    str(args.num_parts)
], check=True)

partition_map = defaultdict(list)
with open(part_file, "r") as f:
    for idx, line in enumerate(f):
        group = int(line.strip())
        node_id = idx + 1
        partition_map[group].append(node_id)

graph, = pydot.graph_from_dot_file(args.dot_input)

with open(mapping_path, "r") as mapfile:
    id_to_node = json.load(mapfile)

node_to_id = {v: int(k) for k, v in id_to_node.items()}

COLORS = [
    "red", "blue", "green", "orange", "purple", "cyan", "gold",
    "brown", "pink", "gray", "olive", "magenta", "teal", "lime"
]
color_lookup = defaultdict(lambda: COLORS[len(color_lookup) % len(COLORS)])

missing_nodes = []
for node in graph.get_nodes():
    raw_name = node.get_name().strip('"').strip()
    if raw_name not in node_to_id:
        missing_nodes.append(raw_name)
        continue
    node_id = node_to_id[raw_name]

    found = False
    for group, node_ids in partition_map.items():
        if node_id in node_ids:
            color = color_lookup[group]
            node.set_fillcolor(color)
            node.set_style("filled")
            node.set_fontcolor("white")
            node.set_label(raw_name)
            found = True
            break
    if not found:
        missing_nodes.append(raw_name)

if missing_nodes:
    print(f"[!] Warning: {len(missing_nodes)} node(s) not found in partition map: {missing_nodes}")
else:
    print("[✓] All DOT nodes matched with partition groups.")

graph.write_raw(args.dot_output)
print(f"[✓] Colored DOT file written to {args.dot_output}")

if args.view:
    pdf_path = args.dot_output + ".pdf"
    try:
        subprocess.run(["dot", "-Tpdf", args.dot_output, "-o", pdf_path], check=True)
        subprocess.run(["open", pdf_path])
        print(f"[✓] PDF view launched: {pdf_path}")
    except Exception as e:
        print(f"[!] Failed to render DOT file: {e}")
