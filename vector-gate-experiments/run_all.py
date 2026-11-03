# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Flyxion
from exp_mapping import run as mapping
from exp_order import run as order
from exp_readout import run as readout
from exp_entanglement import run as entanglement

if __name__ == '__main__':
    for run in (mapping,order,readout,entanglement):
        run()
