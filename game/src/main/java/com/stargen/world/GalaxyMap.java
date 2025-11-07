package com.stargen.world;

import java.util.*;
import com.stargen.engine.simulation.WorldState;

public class GalaxyMap {
    private final List<StarSystem> systems = new ArrayList<>();
    private final WorldState world;

    public GalaxyMap(int n, WorldState world){
        this.world = world;
        Random rng = new Random(7);
        for (int i=0;i<n;i++){
            float phi = 0.5f + rng.nextFloat();
            float S = 0.2f + rng.nextFloat()*0.4f;
            systems.add(new StarSystem(i, phi, S));
        }
    }

    public StarSystem get(int idx){ return systems.get(idx); }
    public int size(){ return systems.size(); }
}
