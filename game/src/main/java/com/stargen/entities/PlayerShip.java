package com.stargen.entities;

import com.stargen.math.Vector3D;

public class PlayerShip extends Entity {
    private final float thrustPower;
    private final float rotationPower;
    private boolean isThrusting = false;
    private Vector3D currentThrust = new Vector3D(0,0,0);

    // RSVP coupling parameters controlled by world:
    private float handlingWobble = 0f;    // 0..0.6 random torque
    private float thrustScale = 1.0f;     // 0.5..1.5

    public PlayerShip(Vector3D start, float thrustPower, float rotationPower){
        super(start);
        this.thrustPower = thrustPower;
        this.rotationPower = rotationPower;
    }

    public void setHandling(float wobble, float thrustScale){
        this.handlingWobble = wobble;
        this.thrustScale = thrustScale;
    }

    public void applyThrust(Vector3D direction){
        Vector3D d = direction.normalize().multiply(thrustPower * thrustScale);
        currentThrust = d;
        isThrusting = true;
    }

    public void stopThrust(){
        currentThrust = new Vector3D(0,0,0);
        isThrusting = false;
    }

    public void roll(float intensity){ rotationVelocity.z += intensity * rotationPower; }
    public void pitch(float intensity){ rotationVelocity.x += intensity * rotationPower; }
    public void yaw(float intensity){ rotationVelocity.y += intensity * rotationPower; }

    @Override public void update(float dt){
        if (isThrusting){
            velocity = new Vector3D(
                velocity.x + currentThrust.x * dt,
                velocity.y + currentThrust.y * dt,
                velocity.z + currentThrust.z * dt
            );
        }
        // entropy-induced wobble
        if (handlingWobble > 1e-3){
            rotationVelocity = new Vector3D(
                rotationVelocity.x + (float)(Math.sin(System.nanoTime()*1e-9)*handlingWobble),
                rotationVelocity.y + (float)(Math.cos(System.nanoTime()*1e-9)*handlingWobble),
                rotationVelocity.z + (float)(Math.sin(System.nanoTime()*1e-9*0.7)*handlingWobble)
            );
        }
        super.update(dt);
    }

    public float speed(){ return velocity.length(); }
}
