import numpy as np

class Grid1D:
    """Uniform 1D grid with periodic boundary conditions."""
    def __init__(self, nx=256, length=1.0):
        self.nx = nx
        self.length = length
        self.dx = length / nx
        self.x = np.linspace(0.0, length, nx, endpoint=False)

class Grid2D:
    """Uniform 2D grid with periodic boundary conditions."""
    def __init__(self, nx=128, ny=128, lx=1.0, ly=1.0):
        self.nx = nx
        self.ny = ny
        self.lx = lx
        self.ly = ly
        self.dx = lx / nx
        self.dy = ly / ny
        x = np.linspace(0.0, lx, nx, endpoint=False)
        y = np.linspace(0.0, ly, ny, endpoint=False)
        self.x, self.y = np.meshgrid(x, y, indexing="ij")
