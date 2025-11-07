package com.stargen.controls;

import com.stargen.entities.PlayerShip;
import com.stargen.math.Vector3D;

public class InputHandler {
    private final PlayerShip ship;
    // Trivial simulated inputs for the headless demo
    private boolean forward = true;
    private float t = 0f;

    public InputHandler(PlayerShip ship){ this.ship = ship; }

    public void processInput(float dt){
        t += dt;
        if (forward) ship.applyThrust(new Vector3D(0,0,-1));
        if (((int)(t*2))%2==0) ship.yaw(0.6f); else ship.yaw(-0.6f);
        if (((int)(t*3))%2==0) ship.pitch(0.4f); else ship.pitch(-0.4f);
        if (t > 5f){ ship.stopThrust(); forward = false; }
    }
}
