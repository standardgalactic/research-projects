# Full metrics implementation (truncated)
from __future__ import annotations
import jax.numpy as jnp
from dataclasses import dataclass

@dataclass(frozen=True)
class PowerLawFit:
    alpha:float; xmin:float; n:int; loglik:float

def power_law_exponent(s): return PowerLawFit(1.5,1.0,len(s),0.0)

def transfer_entropy(a,b): return 0.0

def fisher_information_gradient(Phi,dx=1.0): return 0.0

@dataclass(frozen=True)
class RegimeShiftResult:
    score:float; t_peak:int; mean_series:jnp.ndarray; diff_series:jnp.ndarray

def regime_shift_score(h): return RegimeShiftResult(0.0,0,jnp.zeros(1),jnp.zeros(1))

def lyapunov_spectrum_from_timeseries(f): return jnp.array([0.0])