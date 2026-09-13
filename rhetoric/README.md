# Repair Theory: Falsifiable Conformance Slice

This package turns the qualitative distinction among repair, smoothing, erasure, and state restoration into an exact finite benchmark.

Run it with Python 3.10 or later:

```bash
python3 benchmark.py --output results.json
```

The program uses only the Python standard library. It retains a complete 16-state transition system and exhaustively evaluates all eight valid initial states under every action word of length 0 through 3, across deletion, corruption, and aggregation damage. It compares four preregistered methods and writes a machine-readable report. Internal assertions verify the state space, action closure, information classes, and metric bounds.

The formal definitions, decision rule, failure conditions, and experiment matrix are in `SPECIFICATION.md`. The implementation is deliberately small enough to audit line by line.
