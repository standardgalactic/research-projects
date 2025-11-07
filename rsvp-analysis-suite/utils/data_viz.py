"""
data_viz.py

Visualization utilities for the RSVP Analysis Suite (RAS).

Guidelines enforced:
- Use matplotlib (not seaborn)
- Each chart is a single plot (no subplots)
- Do not specify colors/styles unless explicitly requested

This module provides:
- field plotting (imshow) for scalar fields with colorbar
- quiver plot for vector fields
- line plots for diagnostics over time
- surface plot (3D) for scalar fields using matplotlib's mplot3d
- save_fig utility

The functions are lightweight wrappers to get publishable-looking figures quickly
and are intended to be easily modified for aesthetic choices.
"""
from __future__ import annotations
from typing import Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def plot_scalar_field(field: np.ndarray, title: Optional[str] = None, vmin: Optional[float] = None, vmax: Optional[float] = None, cmap: Optional[str] = None, show: bool = True):
    """Plot a 2D scalar field using imshow with colorbar.

    NOTE: we intentionally don't set a default color to allow user choice; pass cmap to override.
    """
    plt.figure()
    plt.imshow(field, origin='lower', vmin=vmin, vmax=vmax)
    plt.colorbar()
    if title:
        plt.title(title)
    if show:
        plt.show()


def plot_vector_field(vx: np.ndarray, vy: np.ndarray, stride: int = 1, title: Optional[str] = None, show: bool = True):
    """Plot a 2D vector field using quiver. Stride defines sampling frequency for arrows."""
    nx, ny = vx.shape
    x = np.arange(0, nx, stride)
    y = np.arange(0, ny, stride)
    X, Y = np.meshgrid(y, x)
    U = vx[::stride, ::stride]
    V = vy[::stride, ::stride]
    plt.figure()
    plt.quiver(X, Y, U, V)
    if title:
        plt.title(title)
    if show:
        plt.show()


def plot_time_series(times: np.ndarray, values: np.ndarray, label: Optional[str] = None, title: Optional[str] = None, show: bool = True):
    """Plot a simple line chart of values over times."""
    plt.figure()
    plt.plot(times, values)
    if label:
        plt.xlabel(label)
    if title:
        plt.title(title)
    if show:
        plt.show()


def plot_surface(field: np.ndarray, title: Optional[str] = None, show: bool = True):
    """3D surface plot for a scalar field; uses matplotlib's mplot3d."""
    nx, ny = field.shape
    X = np.arange(nx)
    Y = np.arange(ny)
    X, Y = np.meshgrid(X, Y)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, field, rstride=1, cstride=1)
    if title:
        ax.set_title(title)
    if show:
        plt.show()


def save_fig(path: str, dpi: int = 150):
    """Save the current matplotlib figure to disk."""
    plt.savefig(path, dpi=dpi, bbox_inches='tight')


if __name__ == "__main__":
    print('data_viz module demo — plotting synthetic fields')
    N = 64
    x = np.linspace(0, 1, N)
    X, Y = np.meshgrid(x, x, indexing='ij')
    field = np.sin(2 * np.pi * X) * np.cos(2 * np.pi * Y)
    plot_scalar_field(field, title='Synthetic field')
    vx = - (Y - 0.5)
    vy = X - 0.5
    plot_vector_field(vx, vy, stride=4, title='Synthetic vector field')

