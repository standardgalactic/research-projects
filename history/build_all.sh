#!/bin/bash

OUT=figures

./run_blender.sh history_dag $OUT
./run_blender.sh crdt_convergence $OUT
./run_blender.sh history_lattice $OUT
./run_blender.sh entropy_collapse $OUT
./run_blender.sh ising_descent $OUT
