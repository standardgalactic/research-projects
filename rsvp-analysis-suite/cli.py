"""
cli.py

Command-line interface for RSVP Analysis Suite (RAS).
Supports:
- creating new experiments
- running demo simulations (ODE, DDE, SDE, RSVP field)
- plotting and saving figures
- computing diagnostics (entropy, phi_RSVP, Fisher info)

Uses argparse to dispatch subcommands.
"""
from __future__ import annotations
import argparse
import sys

from rsvp_analysis_suite.config import default as load_config
from rsvp_analysis_suite.core import rsvp_fields, tiling_entropy, semantic_phase, fpc_dynamics
from rsvp_analysis_suite.utils import data_viz, io_utils


def run_demo():
    print('Running full RSVP Analysis Suite demo...')
    # create synthetic fields
    Phi, S, Vx, Vy = rsvp_fields.create_synthetic_field()
    # compute tiling entropy
    mean_entropy = tiling_entropy.compute_entropy(Phi)
    print('Mean entropy of synthetic field:', mean_entropy)
    # compute phi_RSVP map
    phi_map = semantic_phase.phi_rsvp_map(Phi, S)
    print('phi_RSVP map computed, min/max:', phi_map.min(), phi_map.max())
    # plot results
    data_viz.plot_scalar_field(Phi, title='Phi Field')
    data_viz.plot_scalar_field(S, title='S Field')
    data_viz.plot_scalar_field(phi_map, title='phi_RSVP map')


def create_experiment(name: str):
    path = io_utils.new_experiment(name)
    print(f'Created experiment folder: {path}')


def main():
    parser = argparse.ArgumentParser(description='RSVP Analysis Suite CLI')
    subparsers = parser.add_subparsers(dest='command')

    parser_demo = subparsers.add_parser('demo', help='Run a full demo of RAS modules')
    parser_exp = subparsers.add_parser('new', help='Create a new experiment')
    parser_exp.add_argument('name', type=str, help='Name of the experiment')

    args = parser.parse_args()

    if args.command == 'demo':
        run_demo()
    elif args.command == 'new':
        create_experiment(args.name)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()

