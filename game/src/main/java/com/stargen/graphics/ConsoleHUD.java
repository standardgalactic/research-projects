package com.stargen.graphics;

import com.stargen.engine.simulation.WorldState;

public class ConsoleHUD {
    private double acc=0;
    public void pulse(WorldState w, float dt){
        acc+=dt; if (acc>=1.0){
            acc=0;
            System.out.printf("[HUD] Φ=%.2f S=%.2f λ=%.2f R=%.2f%n",
                w.getPhi(), w.getEntropy(), w.getLambdaCoupling(), w.getR());
        }
    }
}
