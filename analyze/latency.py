import subprocess
import re
import matplotlib.pyplot as plt
import sys
import os
from collections import defaultdict

if len(sys.argv) != 2:
    print(f"Usage: python {os.path.basename(__file__)} path/to/graphfile.graph")
    sys.exit(1)

graph_file = sys.argv[1]
if not os.path.isfile(graph_file):
    print(f"[!] Error: file '{graph_file}' not found.")
    sys.exit(1)

k_values = range(2, 11)
edge_cuts = []
comm_volumes = []
imbalances = []

for k in k_values:
    cmd = [
        "gpmetis",
        "-contig",
        "-ptype=kway",
        graph_file,
        str(k)
    ]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout + result.stderr

        edge_cut_match = re.search(r"Edgecut:\s+(\d+)", output)
        edge_cut = int(edge_cut_match.group(1)) if edge_cut_match else None

        comm_match = re.search(r"communication volume:\s+(\d+)", output)
        comm_vol = int(comm_match.group(1)) if comm_match else None

        if edge_cut is not None and comm_vol is not None:
            edge_cuts.append((k, edge_cut))
            comm_volumes.append((k, comm_vol))
            print(f"k={k}, edge cut={edge_cut}, communication volume={comm_vol}")

            part_file = f"{graph_file}.part.{k}"
            if os.path.exists(part_file):
                with open(part_file, "r") as f:
                    partitions = [int(line.strip()) for line in f]

                group_weights = defaultdict(int)
                with open(graph_file, "r") as f:
                    lines = f.readlines()
                    header = lines[0].strip().split()
                    has_node_weights = header[2] in {"1", "10", "11"}
                    node_lines = lines[1:]

                    for i, line in enumerate(node_lines):
                        tokens = line.strip().split()
                        weight = int(tokens[0]) if has_node_weights else 1
                        group = partitions[i]
                        group_weights[group] += weight

                total_weight = sum(group_weights.values())
                ideal = total_weight / k
                max_weight = max(group_weights.values())
                imbalance = max_weight / ideal
                imbalances.append((k, imbalance))
                print(f"k={k}, imbalance={imbalance:.3f}")
            else:
                print(f"[!] Missing .part.{k} file for imbalance calculation.")

        else:
            print(f"[!] k={k}: missing output\n{output}")

    except Exception as e:
        print(f"Error running gpmetis for k={k}: {e}")

if edge_cuts and comm_volumes and imbalances:
    fig, axs = plt.subplots(1, 3, figsize=(16, 5))

    ks_cut, cuts = zip(*edge_cuts)
    ks_vol, vols = zip(*comm_volumes)
    ks_imb, imbs = zip(*imbalances)

    axs[0].plot(ks_cut, cuts, marker='o')
    axs[0].set_title("Edge Cut vs. k")
    axs[0].set_xlabel("Partitions (k)")
    axs[0].set_ylabel("Edge Cut")
    axs[0].grid(True)

    axs[1].plot(ks_vol, vols, marker='s', color='orange')
    axs[1].set_title("Comm Volume vs. k")
    axs[1].set_xlabel("Partitions (k)")
    axs[1].set_ylabel("Comm Volume")
    axs[1].grid(True)

    axs[2].plot(ks_imb, imbs, marker='^', color='red')
    axs[2].set_title("Imbalance Ratio vs. k")
    axs[2].set_xlabel("Partitions (k)")
    axs[2].set_ylabel("Imbalance")
    axs[2].grid(True)

    fig.suptitle(f"Partition Metrics for {os.path.basename(graph_file)}", fontsize=14)
    plt.tight_layout()
    plt.show()
else:
    print("[!] Not all METIS results available to plot.")
