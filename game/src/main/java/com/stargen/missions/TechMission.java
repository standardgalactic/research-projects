package com.stargen.missions;

import com.stargen.math.Vector3D;
import com.stargen.engine.simulation.WorldState;
import com.stargen.research.*;

public class TechMission extends Mission {
    private final Vector3D center; private final float radius;
    private final WorldState world; private final TechLogic logic; private final TechTree tree;
    private float timer=0f; private final int unlockIndex;

    public TechMission(Vector3D c, float r, WorldState w, TechLogic logic, TechTree tree, int idx){
        this.center=c; this.radius=r; this.world=w; this.logic=logic; this.tree=tree; this.unlockIndex=idx;
    }

    @Override public void tick(float dt){
        if (state!=State.ACTIVE) return;
        // simple proximity timer
        timer += dt;
        if (timer>10f){
            logic.tryUnlock(tree, world, unlockIndex);
            state = State.COMPLETE;
        }
    }

    public Vector3D center(){ return center; }
    public float radius(){ return radius; }
}
