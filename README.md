# METIS Graph Partitioning and Visualization

This project provides a Python-based workflow for partitioning weighted graphs in DOT format using METIS and visualizing the results. Nodes are color-coded by partition, and optional analysis tools allow exploration of edge cuts, communication volume, and partition imbalance across multiple partition counts.

## Quick Start

Use the main driver script to partition and visualize a graph:

```bash
python3 run.py <input_file.dot> <output_file.dot> <number_of_partitions> [-v]
```

**Arguments:**

- `<input_file.dot>`: The input graph in DOT format (must include node and edge weights).
- `<output_file.dot>`: Path to write the partition-colored DOT file.
- `<number_of_partitions>`: Number of partitions (k-way).
- `-v` / `--view`: Optional. Automatically converts the result to PNG and opens it using your system viewer.

**Example:**

```bash
python3 run.py dot_input/3.dot dot_output/3.dot 4 -v
```

This command will:
1. Convert the DOT graph to METIS `.graph` format.
2. Run METIS with:
   ```
   gpmetis -contig -objtype=cut -ptype=kway 4
   ```
3. Parse METIS output to assign partitions.
4. Recolor the DOT nodes by partition.
5. Save the result and optionally open it as an image.

## Requirements

- Python 3.x
- [Graphviz](https://graphviz.org/download/) (provides the `dot` command)
  - macOS: `brew install graphviz`
  - Ubuntu: `sudo apt install graphviz`
- [METIS](http://glaros.dtc.umn.edu/gkhome/metis/metis/overview)
  - Ensure `gpmetis` is available in your system PATH

## Partitioning Details

This project uses METIS with the following command:

```bash
gpmetis -contig -objtype=cut -ptype=kway <input.graph> <k>
```

- `-contig`: Prefer contiguous partitions
- `-objtype=cut`: Optimize for minimal edge cut
- `-ptype=kway`: Direct k-way partitioning

The output `.part.k` file assigns each node to a partition. This is then mapped back to the DOT graph for coloring.

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

## Analyzing Parallelism

Use the `analyze/analyze_parallelism.py` script to analyze the potential for parallelism in a program represented by a DAG:

```bash
python3 analyze/analyze_parallelism.py path/to/dotfile
```
