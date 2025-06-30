import pydot
from collections import defaultdict
import sys

def compute_partition_costs(dot_path):
    graphs = pydot.graph_from_dot_file(dot_path)
    graph = graphs[0]

    partition_costs = defaultdict(int)

    for node in graph.get_nodes():
        attrs = node.get_attributes()
        if 'cost' in attrs and 'fillcolor' in attrs:
            cost = int(attrs['cost'])
            color = attrs['fillcolor']
            partition_costs[color] += cost

    print("Computation Cost by Partition (fillcolor):")
    for color, total in partition_costs.items():
        print(f"{color:12s}: {total}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load.py input.dot")
        sys.exit(1)

    dot_path = sys.argv[1]
    compute_partition_costs(dot_path)
