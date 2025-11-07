package com.stargen.engine.simulation;

import java.util.Random;

public class WorldState {
    private float phi;         // Φ: usable capacity
    private float entropy;     // S: disorder
    private float lambda;      // λ: governance/safety
    private float sigmaDot;    // Σ̇: entropy production
    private float R;           // R = Φ - λS

    // Tunables
    private float productionRate = 0.15f;
    private float dissipationRate = 0.08f;
    private float noiseLevel = 0.02f;
    private final Random rng = new Random(42);

    public WorldState(float phiInit, float sInit, float lambdaInit){
        this.phi = phiInit;
        this.entropy = sInit;
        this.lambda = lambdaInit;
        updateDerived();
    }

    private void updateDerived(){
        this.R = phi - lambda * entropy;
        float noise = (float)(rng.nextGaussian()*0.5f) * noiseLevel;
        this.sigmaDot = Math.max(0f, (productionRate - dissipationRate) + noise);
    }

    public void tick(float dt){
        phi += productionRate * dt * Math.max(0.05f, R);
        entropy += (sigmaDot + noiseLevel) * dt;
        updateDerived();

        if (R < 0.1f) {
            entropy += 0.08f * dt;
            phi *= (1.0f - 0.01f * dt);
            // signal crisis upstream
        }

        phi = Math.max(0f, Math.min(phi, 20f));
        entropy = Math.max(0f, Math.min(entropy, 12f));
    }

    public void adjustLambda(float d){ lambda = Math.max(0f, Math.min(1.5f, lambda + d)); updateDerived(); }
    public void addPhi(float d){ phi = Math.max(0f, phi + d); updateDerived(); }
    public void addEntropy(float d){ entropy = Math.max(0f, entropy + d); updateDerived(); }

    public float getPhi(){ return phi; }
    public float getEntropy(){ return entropy; }
    public float getLambda(){ return lambda; }
    public float getSigmaDot(){ return sigmaDot; }
    public float getR(){ return R; }
}
