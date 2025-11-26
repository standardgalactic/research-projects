
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import jax
import jax.numpy as jnp
from jax import jit, random

from .fields import RSVPFields


@runtime_checkable
class Agent(Protocol):
    """Structural protocol – any object satisfying this can be used in simulation loops."
    """
    def act(self, fields: RSVPFields, key: jax.random.PRNGKey | None) -> RSVPFields: ...


@dataclass(frozen=True)
class BaseAgent:
    """Common functionality shared by all agents.

    Agents operate on a periodic 2D lattice and can sense a local patch
    around their position.
    """
    x: int
    y: int
    strength: float = 1.0
    radius: int = 9
    memory: int = 20

    def _local_slice(self, arr: jnp.ndarray) -> jnp.ndarray:
        """Return local sensory patch centred on (x,y) with periodic boundaries."
        """
        half = self.radius // 2
        h, w = arr.shape
        xs = (jnp.arange(self.x - half, self.x + half + 1) % w)
        ys = (jnp.arange(self.y - half, self.y + half + 1) % h)
        return arr[jnp.ix_(ys, xs)]

    def _local_coords(self) -> jnp.ndarray:
        """Relative coordinates grid in [-half..+half]^2, shape (r,r,2)."
        """
        half = self.radius // 2
        ys, xs = jnp.meshgrid(jnp.arange(-half, half + 1), jnp.arange(-half, half + 1), indexing="ij")
        return jnp.stack([xs, ys], axis=-1)  # (r,r,2)


class AutocatalyticNode(BaseAgent):
    """
    Keystone / pioneer agent.
    Seeks local entropy minima, reinforces trails, builds persistent low-S channels.
    Real-world analogues: redwoods, coral polyps, early Bitcoin adopters.
    """

    @jit
    def act(self, fields: RSVPFields, key: jax.random.PRNGKey | None) -> RSVPFields:
        S_local = self._local_slice(fields.S)
        coords = self._local_coords()
        center = self.radius // 2
        current_S = S_local[center, center]

        flat_S = S_local.reshape(-1)
        flat_coords = coords.reshape(-1, 2)

        # Prefer lower entropy in the neighbourhood
        delta_S = flat_S - current_S
        weights = jnp.exp(-8.0 * delta_S)

        # Strongly suppress very low-entropy (already crystallised) regions
        weights = jnp.where(flat_S < 0.15, 0.0, weights)

        weights_sum = jnp.sum(weights) + 1e-12
        weights = weights / weights_sum

        move = jnp.sum(weights[:, None] * flat_coords, axis=0)

        size = fields.size
        new_x = (self.x + jnp.round(move[0]).astype(jnp.int32)) % size
        new_y = (self.y + jnp.round(move[1]).astype(jnp.int32)) % size

        reduction = self.strength * 0.09 * jnp.exp(-4.0 * current_S)
        Phi_boost = self.strength * 0.04

        new_S = fields.S.at[new_y, new_x].add(-reduction)
        new_Phi = fields.Phi.at[new_y, new_x].add(Phi_boost)

        return fields.replace(S=jnp.clip(new_S, 0.0, 1.0), Phi=new_Phi)


class EntropyPump(BaseAgent):
    """
    Photosynthesis, fossil-fuel plants, universities, star formation.
    Continuously exports entropy off-lattice using external subsidy.
    """

    @jit
    def act(self, fields: RSVPFields, key: jax.random.PRNGKey | None) -> RSVPFields:
        half = self.radius // 2
        h, w = fields.S.shape
        xs = (jnp.arange(self.x - half, self.x + half + 1) % w)
        ys = (jnp.arange(self.y - half, self.y + half + 1) % h)

        yy, xx = jnp.meshgrid(jnp.arange(-half, half + 1), jnp.arange(-half, half + 1), indexing="ij")
        dist = jnp.sqrt(xx**2 + yy**2)
        mask = jnp.where(dist <= self.radius / 2, 1.0, 0.3)

        pump_rate = self.strength * 0.12
        S_patch = fields.S[jnp.ix_(ys, xs)]
        S_patch = S_patch - pump_rate * mask

        new_S = fields.S.at[jnp.ix_(ys, xs)].set(S_patch)
        return fields.replace(S=jnp.clip(new_S, 0.0, 1.0))


class ConstraintBuilder(BaseAgent):
    """
    Beavers, engineers, bureaucracies, termite mounds.
    Freezes high-flow pathways into permanent low-entropy conduits.
    """

    @jit
    def act(self, fields: RSVPFields, key: jax.random.PRNGKey | None) -> RSVPFields:
        vx_local = self._local_slice(fields.vx)
        vy_local = self._local_slice(fields.vy)
        v_mag_local = jnp.sqrt(vx_local**2 + vy_local**2)

        threshold = jnp.percentile(v_mag_local, 85.0)
        high_flow = v_mag_local > threshold

        half = self.radius // 2
        h, w = fields.Phi.shape
        xs = (jnp.arange(self.x - half, self.x + half + 1) % w)
        ys = (jnp.arange(self.y - half, self.y + half + 1) % h)

        Phi_patch = fields.Phi[jnp.ix_(ys, xs)]
        S_patch = fields.S[jnp.ix_(ys, xs)]

        Phi_patch = Phi_patch + high_flow * self.strength * 0.18
        S_patch = S_patch - high_flow * self.strength * 0.04

        new_Phi = fields.Phi.at[jnp.ix_(ys, xs)].set(Phi_patch)
        new_S = fields.S.at[jnp.ix_(ys, xs)].set(S_patch)

        return fields.replace(Phi=new_Phi, S=jnp.clip(new_S, 0.0, 1.0))


class InvasiveParasite(BaseAgent):
    """
    Zebra mussels, viral memes, pump-and-dump traders.
    Injects large entropy bursts, redirects flow for short-term gain.
    """

    @jit
    def act(self, fields: RSVPFields, key: jax.random.PRNGKey | None) -> RSVPFields:
        if key is None:
            key = random.PRNGKey(0)

        key, subkey = random.split(key)

        local_Phi = fields.Phi[self.y % fields.size, self.x % fields.size]
        trigger_prob = jnp.clip(3.0 * (local_Phi - 0.6), 0.0, 0.9)
        do_activate = random.bernoulli(subkey, trigger_prob)

        injection = do_activate * self.strength * 0.45
        new_S = fields.S.at[self.y % fields.size, self.x % fields.size].add(injection)

        # Redirect nearby flow outward from the parasite centre
        half = self.radius // 2
        h, w = fields.vx.shape
        xs = (jnp.arange(self.x - half, self.x + half + 1) % w)
        ys = (jnp.arange(self.y - half, self.y + half + 1) % h)

        yy, xx = jnp.meshgrid(jnp.arange(-half, half + 1), jnp.arange(-half, half + 1), indexing="ij")
        dir_x = -xx.astype(jnp.float32)
        dir_y = -yy.astype(jnp.float32)
        norm = jnp.sqrt(dir_x**2 + dir_y**2) + 1e-6
        dir_x /= norm
        dir_y /= norm

        vx_patch = fields.vx[jnp.ix_(ys, xs)]
        vy_patch = fields.vy[jnp.ix_(ys, xs)]

        vx_patch = vx_patch + do_activate * 0.3 * dir_x
        vy_patch = vy_patch + do_activate * 0.3 * dir_y

        new_vx = fields.vx.at[jnp.ix_(ys, xs)].set(vx_patch)
        new_vy = fields.vy.at[jnp.ix_(ys, xs)].set(vy_patch)

        return fields.replace(
            S=jnp.clip(new_S, 0.0, 1.0),
            vx=new_vx,
            vy=new_vy,
        )


AGENT_CLASSES = {
    "autocatalytic": AutocatalyticNode,
    "pump": EntropyPump,
    "builder": ConstraintBuilder,
    "parasite": InvasiveParasite,
}
