# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Flyxion
"""Toggle only the two-CX preparation block, keeping all other gates fixed."""
from core import circuit, state, expectation, partial_trace, purity, write


def run():
    rows=[]
    for enabled in (False,True):
        s=state(circuit(.37,.71,-.43,entangled=enabled))
        rows.append(dict(entangled=enabled,purity_q0=float(purity(partial_trace(s,[1,2])).real),
                         xxx=expectation(s,'XXX')))
    assert abs(rows[0]['purity_q0']-1)<1e-12
    assert abs(rows[1]['purity_q0']-.5)<1e-12
    write('entanglement',rows,dict(z=.37,x=.71,y=-.43,subsystem='q0',changed_block='CX(2,0), CX(2,1)'))

if __name__ == '__main__':
    run()
