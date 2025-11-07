package com.stargen.missions;

import com.stargen.world.GalaxyMap;
import com.stargen.world.StarSystem;

public class Mission {
    public enum Type { STABILIZE_NODE }

    private final Type type;
    private final GalaxyMap galaxy;
    private final int nodeIndex;
    private float timer = 0f;

    private Mission(Type type, GalaxyMap galaxy, int nodeIndex){
        this.type = type; this.galaxy = galaxy; this.nodeIndex = nodeIndex;
    }

    public static Mission stabilizeNode(GalaxyMap galaxy, int nodeIndex){
        return new Mission(Type.STABILIZE_NODE, galaxy, nodeIndex);
    }

    public void tick(float dt){
        timer += dt;
        if (type == Type.STABILIZE_NODE){
            StarSystem s = galaxy.get(nodeIndex);
            // simple decay of entropy to simulate stabilization
            s.entropy = Math.max(0f, s.entropy - 0.01f * dt);
        }
    }
}
