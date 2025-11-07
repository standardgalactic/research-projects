package com.stargen.world;

public class StarSystem {
    public final int id;
    public float phi;     // regional Φ
    public float entropy; // regional S

    public StarSystem(int id, float phi, float entropy){
        this.id = id; this.phi = phi; this.entropy = entropy;
    }
}
