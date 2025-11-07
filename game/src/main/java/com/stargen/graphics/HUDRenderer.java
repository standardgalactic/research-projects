package com.stargen.graphics;

import com.stargen.engine.simulation.WorldState;
import com.stargen.entities.PlayerShip;

public class HUDRenderer {
    private long lastPrint = 0;

    public void drawTelemetry(WorldState world, PlayerShip ship){
        long now = System.currentTimeMillis();
        if (now - lastPrint > 1000){
            lastPrint = now;
            System.out.printf("HUD | Φ=%.2f S=%.2f λ=%.2f R=%.2f | pos=%s vel=%.2f%n",
                world.getPhi(), world.getEntropy(), world.getLambda(), world.getR(),
                ship.getPosition().toString(), ship.speed());
        }
    }
}
