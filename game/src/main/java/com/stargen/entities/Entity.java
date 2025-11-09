package com.stargen.entities;

import com.stargen.math.Vector3D;

public class Entity {
    protected Vector3D position;
    protected Vector3D velocity;
    protected Vector3D orientation;      // Euler: x=pitch, y=yaw, z=roll
    protected Vector3D rotationVelocity;

    protected float mass = 1.0f;
    protected float linearDrag = 0.98f;
    protected float angularDrag = 0.92f;

    protected float health = 100f;
    protected float radius = 2.0f;
    protected boolean active = true;

    public Entity(Vector3D start){
        this.position = start;
        this.velocity = new Vector3D(0,0,0);
        this.orientation = new Vector3D(0,0,0);
        this.rotationVelocity = new Vector3D(0,0,0);
    }

    public void update(float dt){
        if (!active) return;
        // drag
        velocity = velocity.multiply(linearDrag);
        rotationVelocity = new Vector3D(
            rotationVelocity.x * angularDrag,
            rotationVelocity.y * angularDrag,
            rotationVelocity.z * angularDrag
        );
        // integrate
        position = new Vector3D(
            position.x + velocity.x * dt,
            position.y + velocity.y * dt,
            position.z + velocity.z * dt
        );
        orientation = new Vector3D(
            orientation.x + rotationVelocity.x * dt,
            orientation.y + rotationVelocity.y * dt,
            orientation.z + rotationVelocity.z * dt
        );
    }

    public Vector3D getPosition(){ return position; }
    public Vector3D getOrientation(){ return orientation; }

    public void takeDamage(float dmg){
        health -= dmg;
        if (health <= 0){ active = false; }
    }
    public boolean isActive(){ return active; }
    public float getRadius(){ return radius; }
    public void setRadius(float r){ radius = r; }
    public float getHealth(){ return health; }
    public void setHealth(float h){ health = h; }
}
