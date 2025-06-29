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
edgecut_results = []
commvol_results = []
imbalance_results = []

for k in k_values:
    cmd = [
        "gpmetis",
        "-contig",
        "-ptype=kway",
        "-objtype=cut",
        graph_file,
        str(k)
    ]

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout + result.stderr

        edgecut_match = re.search(r"Edgecut:\s+(\d+)", output)
        if edgecut_match:
            edgecut = int(edgecut_match.group(1))
            edgecut_results.append((k, edgecut))
            print(f"k={k}, Edgecut={edgecut}")
        else:
            print(f"[!] k={k}: no Edgecut found")

        commvol_match = re.search(r"communication volume:\s+(\d+)", output)
        if commvol_match:
            commvol = int(commvol_match.group(1))
            commvol_results.append((k, commvol))
            print(f"k={k}, CommVol={commvol}")
        else:
            print(f"[!] k={k}: no communication volume found")

        # === Compute Imbalance ===
        part_file = f"{graph_file}.part.{k}"
        if os.path.exists(part_file):
            with open(part_file, "r") as pf:
                partition_assignments = [int(line.strip()) for line in pf.readlines()]
                group_weights = defaultdict(int)

                with open(graph_file, "r") as gf:
                    lines = gf.readlines()
                    header = lines[0].strip().split()
                    has_node_weights = header[2] in {"1", "10", "11"}
                    node_lines = lines[1:]

                    for i, line in enumerate(node_lines):
                        tokens = line.strip().split()
                        weight = int(tokens[0]) if has_node_weights else 1
                        group = partition_assignments[i]
                        group_weights[group] += weight

                total_weight = sum(group_weights.values())
                ideal_weight = total_weight / k
                max_weight = max(group_weights.values())
                imbalance = max_weight / ideal_weight
                imbalance_results.append((k, imbalance))
                print(f"k={k}, Imbalance={imbalance:.3f}")
        else:
            print(f"[!] Missing partition file: {part_file}")

    except Exception as e:
        print(f"[!] Error running gpmetis for k={k}: {e}")

# === Plotting ===
if edgecut_results or commvol_results or imbalance_results:
    fig, axs = plt.subplots(1, 3, figsize=(16, 5))

    if edgecut_results:
        ks1, cuts = zip(*edgecut_results)
        axs[0].plot(ks1, cuts, marker='o', color='blue')
        axs[0].set_title("Edge Cut vs. Partitions")
        axs[0].set_xlabel("k")
        axs[0].set_ylabel("Edge Cut")
        axs[0].grid(True)

    if commvol_results:
        ks2, volumes = zip(*commvol_results)
        axs[1].plot(ks2, volumes, marker='s', color='green')
        axs[1].set_title("Comm Volume vs. Partitions")
        axs[1].set_xlabel("k")
        axs[1].set_ylabel("Comm Volume")
        axs[1].grid(True)

    if imbalance_results:
        ks3, imbalances = zip(*imbalance_results)
        axs[2].plot(ks3, imbalances, marker='^', color='red')
        axs[2].set_title("Imbalance Ratio vs. Partitions")
        axs[2].set_xlabel("k")
        axs[2].set_ylabel("Imbalance Ratio")
        axs[2].grid(True)

    fig.suptitle(f"METIS Partitioning Metrics for {os.path.basename(graph_file)}", fontsize=14)
    plt.tight_layout()
    plt.show()
else:
    print("No valid METIS metrics found to plot.")
