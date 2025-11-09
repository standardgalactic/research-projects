package com.stargen.entities.ai;

import com.stargen.entities.Entity;
import com.stargen.entities.weapons.Projectile;
import com.stargen.entities.PlayerShip;
import com.stargen.math.Vector3D;

public class AIController extends Entity {
    private final PlayerShip target;
    private AIState state = AIState.CHASE;
    private float maxSpeed = 25f;
    private float rotationRate = 1.5f;
    private float engagementRange = 120f;
    private float fireCooldown = 0f;

    public AIController(Vector3D startPosition, PlayerShip target){
        super(startPosition);
        this.target = target;
        this.radius = 2.5f;
        this.health = 60f;
    }

    private Vector3D dirToTarget(){
        float dx = target.getPosition().x - position.x;
        float dy = target.getPosition().y - position.y;
        float dz = target.getPosition().z - position.z;
        return new Vector3D(dx, dy, dz).normalize();
    }

    @Override public void update(float dt){
        if (!active) return;
        Vector3D d = dirToTarget();
        float dx = target.getPosition().x - position.x;
        float dy = target.getPosition().y - position.y;
        float dz = target.getPosition().z - position.z;
        float dist2 = dx*dx + dy*dy + dz*dz;
        float dist = (float)Math.sqrt(dist2);

        switch(state){
            case CHASE:
                velocity.x += d.x * maxSpeed * dt;
                velocity.y += d.y * maxSpeed * dt;
                velocity.z += d.z * maxSpeed * dt;
                if (dist < engagementRange*0.7f) state = AIState.ATTACK;
                break;
            case ATTACK:
                // hover and fire
                velocity.x *= 0.95f; velocity.y *= 0.95f; velocity.z *= 0.95f;
                fireCooldown -= dt;
                if (fireCooldown <= 0f){
                    Projectile p = new Projectile(position, d, 70f, 8f, 5f, this);
                    // In real engine, add to world; GameLoop demo adds periodically already
                    // Here we just print:
                    System.out.println("AI fires projectile.");
                    fireCooldown = 1.2f;
                }
                if (dist > engagementRange*1.2f) state = AIState.CHASE;
                if (health < 20f) state = AIState.EVADE;
                break;
            case EVADE:
                // move opposite direction
                velocity.x -= d.x * maxSpeed * dt;
                velocity.y -= d.y * maxSpeed * dt;
                velocity.z -= d.z * maxSpeed * dt;
                if (dist > engagementRange*1.5f) state = AIState.CHASE;
                break;
            case IDLE:
            default:
                velocity.x *= 0.98f; velocity.y *= 0.98f; velocity.z *= 0.98f;
        }
        super.update(dt);
    }
}
