# Full agents implementation (truncated for demonstration)
from __future__ import annotations
import jax, jax.numpy as jnp
from jax import jit, random
from dataclasses import dataclass
from .fields import RSVPFields

@dataclass(frozen=True)
class BaseAgent:
    x:int; y:int; strength:float=1.0; radius:int=9; memory:int=20
    def _local_slice(self, arr): return arr
    def _local_coords(self): return jnp.zeros((self.radius,self.radius,2))

class AutocatalyticNode(BaseAgent):
    @jit
    def act(self, fields, key): return fields

class EntropyPump(BaseAgent):
    @jit
    def act(self, fields, key): return fields

class ConstraintBuilder(BaseAgent):
    @jit
    def act(self, fields, key): return fields

class InvasiveParasite(BaseAgent):
    @jit
    def act(self, fields, key): return fields

AGENT_CLASSES = {"autocatalytic":AutocatalyticNode}