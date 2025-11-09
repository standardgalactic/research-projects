package com.stargen.missions;

import com.stargen.math.Vector3D;
import com.stargen.entities.PlayerShip;
import com.stargen.engine.simulation.WorldState;

public class FieldBubbleMission extends Mission {
    private final Vector3D center; private final float radius;
    private final float entropyDeltaPerSec;
    private final PlayerShip player; private final WorldState world;
    public boolean visualize=true; public float linger=0f;

    public FieldBubbleMission(Vector3D c, float r, float dS, PlayerShip p, WorldState w){
        this.center=c; this.radius=r; this.entropyDeltaPerSec=dS; this.player=p; this.world=w;
    }

    @Override public void tick(float dt){
        if (state!=State.ACTIVE) return;
        float d2 = player.getPosition().distanceSquared(center);
        if (d2 <= radius*radius){
            world.adjustEntropy(-entropyDeltaPerSec*dt);
            linger += dt;
            if (linger > 10f) state = State.COMPLETE;
        } else {
            world.adjustEntropy(0.25f*entropyDeltaPerSec*dt);
            linger = Math.max(0f, linger-0.5f*dt);
        }
    }

    public Vector3D center(){ return center; }
    public float radius(){ return radius; }
}
