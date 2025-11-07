package com.stargen.entities.weapons;

import com.stargen.entities.Entity;
import com.stargen.math.Vector3D;

public class Projectile extends Entity {
    private final float damage;
    private float lifespan;

    public Projectile(Vector3D start, Vector3D direction, float speed, float damage, float lifespan){
        super(start);
        this.velocity = direction.normalize().multiply(speed);
        this.damage = damage;
        this.lifespan = lifespan;
        this.linearDrag = 1.0f;
    }

    @Override public void update(float dt){
        lifespan -= dt;
        if (lifespan <= 0) {
            // would be removed from world in a real engine
            this.linearDrag = 0.0f; // park
        }
        super.update(dt);
    }

    public float getDamage(){ return damage; }
}
