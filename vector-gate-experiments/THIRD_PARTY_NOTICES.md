# Third-party boundaries

The MIT licence in this directory applies to project-controlled material only. Dependencies are installed independently and retain their own copyrights, licences and bundled component notices. This archive contains no vendored third-party source or wheels.

| Component | Use | Upstream terms and notices |
| --- | --- | --- |
| Qiskit | QuantumCircuit, Statevector, Pauli, partial_trace, purity | Apache-2.0; https://github.com/Qiskit/qiskit/blob/main/LICENSE.txt |
| NumPy | Numeric arrays, grid generation and comparisons | BSD-3-Clause, with additional bundled-component notices; https://numpy.org/doc/stable/license.html |
| Python | Runtime and standard library | PSF and component-specific terms; https://docs.python.org/3/license.html |

`requirements-tested.txt` records the installed Qiskit/NumPy versions and their direct supporting packages for repeatable installation. It is not a licence inventory for a redistributed environment, nor a complete lock for all platforms. SciPy, rustworkx, dill, stevedore, typing_extensions, their transitive dependencies and any numerical-library binaries retain their distributed notices. Consult the actual installed distribution metadata before bundling an environment. No claim is made that this MIT notice covers those components.

Upstream references: https://github.com/Qiskit/qiskit and https://github.com/numpy/numpy/blob/main/doc/source/license.rst . Upstream links may change; the installed release's own licence files govern that distribution. No legal conclusion about an unrelated dataset or downstream training corpus is implied.
