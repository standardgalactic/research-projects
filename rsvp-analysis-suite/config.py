"""
config.py

Configuration layer for the RSVP Analysis Suite (RAS).
Centralizes global parameters, environment variables, and default paths.
Allows both file-based (.json/.yaml) and environment overrides.

This module defines:
- Config dataclass with key RAS parameters
- load_config / save_config functions
- env_override to patch parameters from environment variables
- default() singleton to access current config

Extend this module with experiment presets or CLI profiles as needed.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

import os
import json

CONFIG_PATH = os.environ.get('RSVP_CONFIG_PATH', 'rsvp_config.json')


@dataclass
class Config:
    data_root: str = 'experiments'
    log_level: str = 'INFO'
    default_dt: float = 0.01
    random_seed: int = 42
    backend: str = 'numpy'  # future: could support jax, torch
    
    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_config(path: str = CONFIG_PATH) -> Config:
    if not os.path.exists(path):
        return Config()
    with open(path, 'r') as f:
        data = json.load(f)
    return Config(**data)


def save_config(cfg: Config, path: str = CONFIG_PATH):
    with open(path, 'w') as f:
        json.dump(cfg.as_dict(), f, indent=2)


def env_override(cfg: Config) -> Config:
    """Apply environment variable overrides (RSVP_*)."""
    for field in cfg.__dataclass_fields__:
        key = 'RSVP_' + field.upper()
        if key in os.environ:
            val = os.environ[key]
            # attempt to cast numeric types
            try:
                if '.' in val:
                    val = float(val)
                else:
                    val = int(val)
            except Exception:
                pass
            setattr(cfg, field, val)
    return cfg


_default_cfg: Optional[Config] = None


def default() -> Config:
    global _default_cfg
    if _default_cfg is None:
        _default_cfg = env_override(load_config())
    return _default_cfg


if __name__ == "__main__":
    print('config demo — loading default config')
    cfg = default()
    print(cfg)
    save_config(cfg)
    print('Saved to', CONFIG_PATH)

