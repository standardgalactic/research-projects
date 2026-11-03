# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Flyxion
"""Hold phase-only states fixed and change only Z versus X readout."""
import numpy as np
from core import circuit, state, expectation, tv, write


def run():
    rows=[]
    reference=state(circuit(0,0,0)).probabilities()
    for z in np.linspace(0,np.pi,17):
        qc=circuit(z,0,0)
        s=state(qc)
        readout=qc.copy()
        for q in range(3):
            readout.h(q)
        p=state(readout).probabilities()
        parity=sum((-1)**i.bit_count()*p[i] for i in range(8))
        rows.append(dict(z=float(z),z_basis_tv=tv(s.probabilities(),reference),
                         xxx=expectation(s,'XXX'),x_readout_parity=float(parity),expected=float(np.cos(2*z))))
    assert max(r['z_basis_tv'] for r in rows)<1e-12
    assert max(abs(r['xxx']-r['expected']) for r in rows)<1e-12
    assert max(abs(r['xxx']-r['x_readout_parity']) for r in rows)<1e-12
    write('readout',rows,dict(x=0,y=0,z_points=17,readout='exact probabilities'))

if __name__ == '__main__':
    run()
