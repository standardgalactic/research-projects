# Vector gate experiments

A small controlled experiment family developed from Flyxion's `RSVP-Monograph/rsvp_quantum_vector_gates.py`. These are ideal three-qubit circuit experiments, not evidence for a physical RSVP theory, quantum advantage, a useful learned representation, or performance on hardware. No training dataset or training pipeline is included.

## Run

Use Python 3.10 or newer in an isolated environment, from this directory:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-tested.txt
python run_all.py
```

Alternatively install `requirements.txt` for the declared major-version ranges. Only the exact versions recorded in `requirements-tested.txt` were exercised here. Qiskit supplies the circuit and statevector APIs; no Aer installation, IBM account, network access at execution time, or hardware backend is needed. Each `exp_*.py` also runs independently. Every run overwrites its own JSON in `results/`, with parameters and Python, NumPy and Qiskit versions. Results are deliberately retained in the package. Run without Python's `-O` option to keep the analytic assertions enabled.

## Design

The reference preparation is H(2), CX(2,0), CX(2,1), followed by RZ(z) on qubits 0 and 1, RX(x) on qubit 0 and RY(y) on qubit 1. This preserves the source circuit's gate order. Angles are radians. Every comparison holds all parameters fixed except its named factor; phase sweeps repeat that comparison at each value.

| Script | One changed feature | Question and diagnostic |
| --- | --- | --- |
| `exp_mapping.py` | Cartesian versus polar expression of the angle map | Are the encodings actually distinct? Compare angle error and state infidelity on an 81-vector grid, including zero and magnitudes above one. |
| `exp_order.py` | Scalar block before versus after the vector block | Does noncommuting order change the state? Compare state infidelity and computational-basis total variation at 17 scalar angles. |
| `exp_readout.py` | Z versus X measurement basis | Can phase be present but absent from population measurements? With vector angles zero, compare phase-invariant Z probabilities against X-parity, whose expectation is cos(2z). |
| `exp_entanglement.py` | Presence of the two-CX preparation block | Does this preparation create entanglement? Compare reduced q0 purity with and without that block, keeping H and all encoding gates fixed. |

The linear map is x = alpha vx / scale, y = alpha vy / scale. The polar expression is exactly the same map by r cos(phi) = vx / scale and r sin(phi) = vy / scale, including at large magnitudes. It is a negative control, not a second encoder. Unlike the source's denominator `scale + 1e-12`, the adaptation validates a strictly positive scale and divides by it directly. Scaling is not unit-norm normalization or clipping. Rotation periodicity prevents assuming this is an injective vector representation.

Infidelity is 1 - |<a|b>|², so global phase is ignored. Total variation is half the L1 distance between probability vectors. Qiskit Pauli labels and output bitstrings read q2, q1, q0 from left to right. X readout applies H on each qubit before taking Z probabilities; its parity equals <XXX>. Each RZ contributes z to the GHZ relative phase, producing the factor 2z. Purity Tr(rho0²) equals 1 for the product control and 1/2 for the entangled preparation; subsequent local rotations preserve it. The entanglement control tests the entire preparation block, not the marginal effect of either individual CX.

## Validation and interpretation

`run_all.py` checks mapping equivalence, the zero-phase order control, a nonzero order effect, the phase/readout identity and both purity values against analytic expectations with tolerance 1e-12. These checks passed on the versions recorded in the JSON outputs. The mapping maximum angle discrepancy was below 2e-15, and maximum infidelity below 2e-15. At z = pi, swapping block order produced infidelity about 0.525 while Z-basis total variation remained zero. This demonstrates why a state change need not appear in the chosen readout.

All probabilities are exact ideal-state simulation values. There are no shots, confidence intervals, device noise, transpilation comparisons or performance benchmarks. Synthetic JSON rows may support small evaluation exercises, but do not establish generalization or training utility. Keep numerical-equivalence controls together if constructing a later train/test split to avoid treating equivalent encoders as independent examples.

## Provenance and licensing

The starting source is [the vector-gate example](https://github.com/standardgalactic/research-projects/blob/main/RSVP-Monograph/rsvp_quantum_vector_gates.py), retrieved November 3, 2026 with Git blob SHA `0e255690b5d21363cde40e097db8b107b57ddbc2`. The retrieved repository LICENSE blob was `74a0d13f28a07f492f89eb5b6406a1e267ece5f6`. These identify the inspected bytes; the main-branch links can change. [Issue #3](https://github.com/standardgalactic/research-projects/issues/3) supplies the reuse context. The cited older source version was commit `d2b52f2a321fa54f727d3ba179bd4e9b8f23c5a4`; this suite derives from the corrected current source inspected above, rather than claiming a separate audit of that historical commit.

`core.py` adapts the project-owned circuit structure and angle-map idea. The experiment drivers, validation, documentation and generated synthetic results are new project material. Their licence is MIT under the complete notice in `LICENSE`, retaining Copyright (c) 2025 Flyxion and adding 2026 Flyxion for this suite. All Python files carry SPDX identifiers. No Qiskit or NumPy implementation files, documentation excerpts, binaries, or external datasets are bundled. Imports call separately installed software and do not relicense it.

See `THIRD_PARTY_NOTICES.md` for external boundaries. Research, redistribution and model training or evaluation of project material are subject to the MIT notice; this package grants no additional rights in external software or datasets.
