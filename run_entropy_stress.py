#!/usr/bin/env python3
"""
run_entropy_stress.py
---------------------
Batch runner for RSVP entropy–field experiments.

Performs a sweep of the coupling parameter λ and logs results
(average Σ̇ and coherence proxy) to a JSONL file for downstream
analysis (meta_analysis.py, governance_metrics.py, etc.).

Usage:
  python run_entropy_stress.py --lmin 0.0 --lmax 1.0 --nsteps 21 --outfile logs/entropy_stress.jsonl
"""
import argparse, json, os
import numpy as np
from datetime import datetime
from dataclasses import dataclass
rng = np.random.default_rng(42)

@dataclass
class Config:
    nx: int = 64
    ny: int = 64
    dt: float = 0.05
    steps: int = 200
    diffusion_phi: float = 0.2
    diffusion_s: float = 0.15
    noise_scale: float = 0.02

def roll2(a, dx, dy): return np.roll(np.roll(a, dx, 0), dy, 1)
def grad(a): return 0.5*(roll2(a,1,0)-roll2(a,-1,0)),0.5*(roll2(a,0,1)-roll2(a,0,-1))
def laplacian(a): return roll2(a,1,0)+roll2(a,-1,0)+roll2(a,0,1)+roll2(a,0,-1)-4*a
def divergence(ax,ay): return 0.5*(roll2(ax,1,0)-roll2(ax,-1,0))+0.5*(roll2(ay,0,1)-roll2(ay,0,-1))

def init_fields(cfg):
    X,Y=np.meshgrid(np.linspace(-1,1,cfg.nx),np.linspace(-1,1,cfg.ny),indexing='ij')
    Phi=1+0.5*np.exp(-3*(X**2+Y**2))+0.05*rng.standard_normal((cfg.nx,cfg.ny))
    S=0.8+0.1*rng.standard_normal((cfg.nx,cfg.ny))
    vx,vy=0.2*(-Y)+0.02*rng.standard_normal((cfg.nx,cfg.ny)),0.2*(X)+0.02*rng.standard_normal((cfg.nx,cfg.ny))
    return Phi,S,vx,vy

def step(Phi,S,vx,vy,cfg,lam):
    R=Phi-lam*S
    dRx,dRy=grad(R)
    vx=vx-cfg.dt*dRx+0.05*laplacian(vx)
    vy=vy-cfg.dt*dRy+0.05*laplacian(vy)
    adv_phi=divergence(Phi*vx,Phi*vy)
    adv_s=divergence(S*vx,S*vy)
    Phi=Phi-cfg.dt*adv_phi+cfg.diffusion_phi*laplacian(Phi)+cfg.noise_scale*rng.standard_normal(Phi.shape)
    S=S-cfg.dt*adv_s+cfg.diffusion_s*laplacian(S)+cfg.noise_scale*rng.standard_normal(S.shape)
    dSx,dSy=grad(S)
    sigma_dot=float(np.mean(dSx*vx+dSy*vy))
    coh=-float(np.mean(dRx**2+dRy**2))
    return Phi,S,vx,vy,sigma_dot,coh

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--lmin',type=float,default=0.0)
    p.add_argument('--lmax',type=float,default=1.0)
    p.add_argument('--nsteps',type=int,default=21)
    p.add_argument('--outfile',type=str,default='entropy_stress.jsonl')
    args=p.parse_args()
    cfg=Config()
    os.makedirs(os.path.dirname(args.outfile) or '.',exist_ok=True)
    with open(args.outfile,'w') as f:
        for lam in np.linspace(args.lmin,args.lmax,args.nsteps):
            Phi,S,vx,vy=init_fields(cfg)
            sigmas=[];cohs=[]
            for _ in range(cfg.steps):
                Phi,S,vx,vy,sdot,coh=step(Phi,S,vx,vy,cfg,lam)
                sigmas.append(sdot);cohs.append(coh)
            record={'lambda':float(lam),
                    'sigma_mean':float(np.mean(sigmas[-50:])),
                    'coherence_mean':float(np.mean(cohs[-50:])),
                    'timestamp':datetime.utcnow().isoformat()+'Z'}
            f.write(json.dumps(record)+'\n')
            print(f"λ={lam:.3f} -> Σ̇={record['sigma_mean']:.4f}, coherence={record['coherence_mean']:.4f}")

if __name__=='__main__': main()
