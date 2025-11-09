package com.stargen.world;

import java.util.Random;

/** Descent-like tunnel generator using box-carves through a filled voxel field. */
public class TunnelGenerator {
    public TunnelLevel generate(long seed, int W, int H, int D, int segments){
        Random rng = new Random(seed);
        TunnelLevel lvl = new TunnelLevel(W,H,D);
        int cx = W/2, cy = H/2, cz = D/2;
        int rad = Math.min(Math.min(W,H),D)/12;
        for(int i=0;i<segments;i++){
            int nx = clamp(cx + rng.nextInt(rad*4+1)-2*rad, rad, W-rad-1);
            int ny = clamp(cy + rng.nextInt(rad*4+1)-2*rad, rad, H-rad-1);
            int nz = clamp(cz + rng.nextInt(rad*4+1)-2*rad, rad, D-rad-1);
            int sx = Math.min(cx, nx), ex = Math.max(cx, nx);
            int sy = Math.min(cy, ny), ey = Math.max(cy, ny);
            int sz = Math.min(cz, nz), ez = Math.max(cz, nz);
            lvl.carveBox(sx-rad, sy-rad, sz-rad, ex+rad, ey+rad, ez+rad);
            cx=nx;cy=ny;cz=nz;
        }
        return lvl;
    }
    private int clamp(int v,int a,int b){ return Math.max(a, Math.min(b, v)); }
}
