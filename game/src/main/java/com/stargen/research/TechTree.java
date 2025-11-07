package com.stargen.research;

import java.util.*;
import com.stargen.engine.simulation.WorldState;

public class TechTree {
    private final List<Technology> techs = new ArrayList<>();
    private final WorldState world;

    public TechTree(WorldState world){
        this.world = world;
        techs.add(new Technology("Efficient Supply Routing", 0.20f, -0.10f,  0.05f));
        techs.add(new Technology("Adaptive AI Schedulers",   0.30f,  0.10f, -0.08f));
        techs.add(new Technology("Constitutional Safety Layer", -0.05f, -0.20f, 0.12f));
        techs.add(new Technology("Quantum Refinery Systems", 0.40f,  0.05f, -0.10f));
    }

    public void unlock(String name){
        for (Technology t : techs){
            if (t.name.equals(name) && !t.unlocked){
                t.unlocked = true;
                world.addPhi(t.dPhi);
                world.addEntropy(t.dS);
                world.adjustLambda(t.dLambda);
                System.out.println("🔧 Tech Unlocked: " + name);
                return;
            }
        }
        System.out.println("Tech not found or already unlocked: " + name);
    }

    public List<Technology> list(){ return techs; }
}
