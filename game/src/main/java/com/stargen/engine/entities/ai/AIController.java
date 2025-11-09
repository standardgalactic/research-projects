package com.stargen.engine.entities.ai;

import com.stargen.entities.Entity;
import com.stargen.entities.Damageable;
import com.stargen.entities.weapons.Projectile;
import com.stargen.entities.PlayerShip;
import com.stargen.math.Vector3D;

public class AIController extends Entity {
    private final PlayerShip target;
    private AIState currentState = AIState.CHASE;
    private final float maxSpeed = 25.0f;
    private final float rotationRate = 1.5f;
    private final float engagementRange = 100.0f;

    public AIController(Vector3D startPosition, PlayerShip target){
        super(startPosition);
        this.target = target;
        this.radius = 0.6f;
    }

    public Vector3D calculateDirectionToTarget(){
        float dx = target.getPosition().x - this.getPosition().x;
        float dy = target.getPosition().y - this.getPosition().y;
        float dz = target.getPosition().z - this.getPosition().z;
        return new Vector3D(dx,dy,dz).normalized();
    }

    @Override public void update(float dt){
        Vector3D dir = calculateDirectionToTarget();
        // Distance (approx) from normalized vector not ideal; use actual distance for behavior switching
        // but keep it simple here.
        switch (currentState) {
            case CHASE:
                velocity.x += dir.x * maxSpeed * dt;
                velocity.y += dir.y * maxSpeed * dt;
                velocity.z += dir.z * maxSpeed * dt;
                break;
            case ATTACK:
                velocity.x *= 0.9f; velocity.y *= 0.9f; velocity.z *= 0.9f;
                break;
            default:
                break;
        }
        super.update(dt);
    }
}
