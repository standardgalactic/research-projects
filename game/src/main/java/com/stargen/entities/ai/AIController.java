package com.stargen.entities.ai;

import com.stargen.entities.Entity;
import com.stargen.entities.PlayerShip;
import com.stargen.math.Vector3D;

public class AIController extends Entity {
    private final PlayerShip target;
    private AIState state = AIState.CHASE;
    private final float maxSpeed = 25.0f;
    private final float rotationRate = 1.2f;
    private final float engageRange = 100.0f;

    public AIController(Vector3D start, PlayerShip target){
        super(start);
        this.target = target;
    }

    private Vector3D dirToTarget(){
        Vector3D d = new Vector3D(
            target.getPosition().x - position.x,
            target.getPosition().y - position.y,
            target.getPosition().z - position.z
        );
        return d.normalize();
    }

    @Override public void update(float dt){
        Vector3D d = dirToTarget();
        float dist2 = (float)Math.max(1e-6, Math.pow(target.getPosition().x - position.x,2) +
                                         Math.pow(target.getPosition().y - position.y,2) +
                                         Math.pow(target.getPosition().z - position.z,2));
        switch(state){
            case CHASE:
                if (dist2 > engageRange*engageRange) {
                    velocity = velocity.add(d.multiply(maxSpeed * dt));
                } else state = AIState.ATTACK;
                break;
            case ATTACK:
                velocity = velocity.multiply(0.9f);
                // placeholder for firing behavior
                break;
            default: break;
        }
        super.update(dt);
    }
}
