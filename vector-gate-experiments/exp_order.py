# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Flyxion
"""Change only placement of scalar rotations relative to vector rotations."""
import numpy as np
from core import circuit, state, infidelity, tv, write


def run():
    rows=[]
    for z in np.linspace(0, np.pi, 17):
        a=state(circuit(z,.71,-.43))
        b=state(circuit(z,.71,-.43,order='vector_then_z'))
        rows.append(dict(z=float(z),infidelity=infidelity(a,b),z_basis_tv=tv(a.probabilities(),b.probabilities())))
    assert rows[0]['infidelity'] < 1e-12
    assert max(r['infidelity'] for r in rows) > .01
    write('order',rows,dict(x=.71,y=-.43,z_points=17))

if __name__ == '__main__':
    run()
