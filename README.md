# METIS Graph Partitioning and Visualization

This project provides a Python-based workflow for partitioning weighted graphs in DOT format using METIS and SCOTCH and visualizing the results. Nodes are color-coded by partition, and optional analysis tools allow exploration of edge cuts, communication volume, and partition imbalance across multiple partition counts.

## Using METIS via `metis.py`

Use the main driver script to partition and visualize a graph:

```bash
python3 metis.py <input_file.dot> <output_file.dot> <number_of_partitions> [-v]
```

**Arguments:**

- `<input_file.dot>`: The input graph in DOT format (must include node and edge weights).
- `<output_file.dot>`: Path to write the partition-colored DOT file.
- `<number_of_partitions>`: Number of partitions (k-way).
- `-v` / `--view`: Optional. Automatically converts the result to PNG and opens it using your system viewer.

**Example:**

```bash
python3 metis.py dot_input/3.dot dot_output/3.dot 4 -v
```

This command will:
1. Convert the DOT graph to METIS `.graph` format.
2. Run METIS with:

   ```bash
   gpmetis -contig -objtype=cut -ptype=kway 4
   ```

3. Parse METIS output to assign partitions.
4. Recolor the DOT nodes by partition.
5. Save the result and optionally open it as an image.

---

## Using SCOTCH via `gmap.py`

For hierarchical or topology-aware partitioning (e.g., CPU/GPU clusters), use SCOTCH with the `gmap` command. The provided `gmap.py` script handles conversion, partitioning, and visualization.

```bash
python3 gmap.py <input_file.dot>
```

**Arguments:**

- `<input_file.dot>`: The input graph in DOT format with node and edge `cost` attributes.
- `hardware.arch`: Must be present in the root directory. Describes the hardware topology (processors and links).

**What it does:**
1. Converts the DOT graph to SCOTCH `.grf` format (stored in `/scotch`).
2. Runs `gmap` to partition the graph based on the topology described in `hardware.arch`.
3. Produces a `.map` file (in `/scotch`) mapping each node to a processor.
4. Recolors the original DOT graph by partition and saves it to `/dot_output`.

**Example Output Files:**

- `scotch/<basename>.grf`: Input graph in SCOTCH format
- `scotch/<basename>.map`: Partition mapping output by `gmap`
- `dot_output/<basename>.mapped.dot`: Colorized DOT graph showing partition assignment

**Dependencies:**

- `gmap` (part of the SCOTCH toolset) must be installed and available in PATH
- A valid `hardware.arch` file describing processor topology

---

## Requirements

- Python 3.x
- [Graphviz](https://graphviz.org/download/) (provides the `dot` command)
  - macOS: `brew install graphviz`
  - Ubuntu: `sudo apt install graphviz`
- [METIS](http://glaros.dtc.umn.edu/gkhome/metis/metis/overview) – required for METIS mode
- [SCOTCH](https://gitlab.inria.fr/scotch/scotch) – required for SCOTCH mode (`gmap`)

---

## Partition Quality Analysis

Use the `analyze/latency.py` script to analyze partition metrics over a range of k values (from 2 to 10):

```bash
python3 analyze/latency.py path/to/graphfile.graph
```

This will:

- Run METIS repeatedly with `k = 2...10`
- Extract the following metrics from each run:
  - Edge Cut
  - Communication Volume
  - Partition Imbalance (based on node weights)
- Plot the results using `matplotlib`

Three graphs will be shown:

- Edge Cut vs. Partitions
- Communication Volume vs. Partitions
- Imbalance Ratio vs. Partitions

---

## Analyzing Parallelism

Use the `analyze/analyze_parallelism.py` script to analyze the potential for parallelism in a program represented by a DAG:

```bash
python3 analyze/analyze_parallelism.py path/to/dotfile
```

This will compute:

- Total computation work
- Critical path (span)
- Parallelism ratio
- Stage-wise slackness

---
