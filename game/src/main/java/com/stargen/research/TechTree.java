package com.stargen.research;

import java.util.*;

import java.util.*;
import com.stargen.engine.simulation.WorldState;

public class TechTree {
    private final TechLogic logic = new TechLogic();
    private final List<Technology> techs = new ArrayList<>();
    private final WorldState world;

    public TechTree(WorldState world){
    private final TechLogic logic = new TechLogic();
        this.world = world;
        techs.add(new Technology("Efficient Supply Routing", 0.20f, -0.10f,  0.05f));
        techs.add(new Technology("Adaptive AI Schedulers",   0.30f,  0.10f, -0.08f));
        techs.add(new Technology("Constitutional Safety Layer", -0.05f, -0.20f, 0.12f));
        techs.add(new Technology("Quantum Refinery Systems", 0.40f,  0.05f, -0.10f));
    }

    public void unlock(String techName){
        // Back-end enforcement of prerequisites/tier via TechLogic
        Set<String> unlocked = new HashSet<>();
        for (Technology t : techs){ if (t.unlocked) unlocked.add(t.name); }
        if (!logic.canUnlock(techName, unlocked)){
            System.out.println("[TechTree] Prerequisites not met for: " + techName);
            return;
        }
        for (Technology t : techs){
            if (t.name.equals(techName) && !t.unlocked){
                t.unlocked = true;
                world.adjustLambda(t.dLambda);
                world.addPhi(t.dPhi);
                world.addEntropy(t.dS);
                System.out.println("[TechTree] Unlocked: " + techName);
                return;
            }
        }
        System.out.println("[TechTree] Tech not found or already unlocked: " + techName);
    }
        }
        System.out.println("Tech not found or already unlocked: " + name);
    }

    public List<Technology> list(){ return techs; }
}
