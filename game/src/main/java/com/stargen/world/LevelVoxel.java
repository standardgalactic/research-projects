package com.stargen.world;

public class LevelVoxel {
    public final int x, y, z;
    public boolean solid;
    public LevelVoxel(int x, int y, int z, boolean solid){
        this.x=x; this.y=y; this.z=z; this.solid=solid;
    }
}
