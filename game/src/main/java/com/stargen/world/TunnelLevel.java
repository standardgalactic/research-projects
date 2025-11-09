package com.stargen.world;

import java.util.*;

public class TunnelLevel {
    public final int W, H, D;
    public final boolean[][][] solid;

    public TunnelLevel(int W, int H, int D){
        this.W=W; this.H=H; this.D=D;
        this.solid = new boolean[W][H][D];
        for(int x=0;x<W;x++) for(int y=0;y<H;y++) for(int z=0;z<D;z++) solid[x][y][z]=true; // start filled
    }

    public void carveBox(int x0,int y0,int z0,int x1,int y1,int z1){
        for(int x=Math.max(0,x0); x<Math.min(W,x1); x++)
        for(int y=Math.max(0,y0); y<Math.min(H,y1); y++)
        for(int z=Math.max(0,z0); z<Math.min(D,z1); z++){
            solid[x][y][z]=false;
        }
    }

    public int solidCount(){
        int c=0;
        for(int x=0;x<W;x++) for(int y=0;y<H;y++) for(int z=0;z<D;z++) if (solid[x][y][z]) c++;
        return c;
    }
}
