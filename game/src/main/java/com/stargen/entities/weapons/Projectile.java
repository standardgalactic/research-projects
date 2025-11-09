package com.stargen.entities.weapons;

import com.stargen.entities.Entity;
import com.stargen.math.Vector3D;

public class Projectile extends Entity {
    private final float damage;
    private float lifespan;
    private final int ownerHash;

    public Projectile(Vector3D start, Vector3D direction, float speed, float damage, float lifespan, Entity owner){
        super(start);
        this.velocity = direction.normalize().multiply(speed);
        this.damage = damage;
        this.lifespan = lifespan;
        this.linearDrag = 1.0f;
        this.radius = 0.5f;
        this.ownerHash = owner == null ? 0 : System.identityHashCode(owner);
    }

    @Override public void update(float dt){
        if (!active) return;
        lifespan -= dt;
        if (lifespan <= 0) {
            active = false;
            return;
        }
        super.update(dt);
    }

    public float getDamage(){ return damage; }
    public int getOwnerHash(){ return ownerHash; }
}
