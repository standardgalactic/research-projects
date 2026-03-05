# History Computation Visualizations

This repository contains scripts used to generate visualizations for research into **history-based models of computation**.
The figures illustrate structures such as event histories, merge operations, constraint dynamics, and history lattices.

## Online Visualizer

You can explore the rendered visualizations in a retro terminal-style viewer here:

**https://standardgalactic.github.io/research-projects/history/**

The page displays generated figures from this repository, including:

* History DAGs
* History lattices
* CRDT convergence structures
* Entropy collapse visualizations
* Constraint-descent (Ising-style) dynamics

## Repository Structure

```
history/
├── branch_and_merge.py
├── build_all.sh
├── event_history_growth.py
├── figure_factory.py
├── run_blender.sh
├── scene_utils.py
├── scenes_history_dag.py
├── scenes_history_lattice.py
├── scenes_crdt_convergence.py
├── scenes_entropy_collapse.py
├── scenes_ising_descent.py
├── figures/
└── out/
```

### Key Components

* **figure_factory.py**
  Main entry point used by Blender to build a visualization scene.

* **scenes_*.py**
  Individual visualization generators for specific conceptual models.

* **scene_utils.py**
  Shared Blender helper utilities for geometry, cameras, lighting, and layout.

* **run_blender.sh**
  Runs a single scene and exports both a `.blend` file and a rendered `.png`.

* **build_all.sh**
  Builds all visualization figures in one step.

## Generating the Figures

Requirements:

* Blender (tested with Blender 3.x)
* Python 3

Generate all figures:

```bash
./build_all.sh
```

This will produce rendered images in:

```
figures/
```

and additional outputs in:

```
out/
```

Each visualization is also saved as a `.blend` file for further editing.

## Viewing Results Locally

You can view the results in the browser:

```
index.html
```

or by running a simple local server:

```bash
python -m http.server
```

Then open:

```
http://localhost:8000
```

## Purpose

These visualizations support research exploring a computational framework where:

* **Histories are the primary objects of computation**
* **Execution corresponds to history extension**
* **Composition corresponds to history merge**
* **Abstraction corresponds to reduction of histories**

The generated figures provide visual intuition for these structures.

