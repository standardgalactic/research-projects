# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Flyxion
"""Change only Cartesian versus polar expression of the angle map."""
import numpy as np
from core import angles, circuit, state, infidelity, write


def run():
    rows = []
    for x in np.linspace(-2, 2, 9):
        for y in np.linspace(-2, 2, 9):
            a, b = angles(x, y), angles(x, y, mapping='polar')
            rows.append(dict(vx=float(x), vy=float(y), angle_error=float(np.max(np.abs(np.subtract(a,b)))),
                             infidelity=infidelity(state(circuit(.37,*a)), state(circuit(.37,*b)))))
    assert max(r['angle_error'] for r in rows) < 1e-12
    assert max(r['infidelity'] for r in rows) < 1e-12
    write('mapping', rows, dict(grid='9x9 over [-2,2]^2', scale=1, alpha=float(np.pi), z=.37))

if __name__ == '__main__':
    run()
