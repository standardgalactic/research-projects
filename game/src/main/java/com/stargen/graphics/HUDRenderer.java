package com.stargen.graphics;

import com.stargen.engine.simulation.WorldState;

public class HUDRenderer {
    private static String bar(float v, float min, float max, int width){
        float t = (v - min) / (max - min);
        if (t < 0f) t = 0f; if (t > 1f) t = 1f;
        int n = Math.round(t * width);
        StringBuilder sb = new StringBuilder("[");
        for (int i=0;i<width;i++) sb.append(i < n ? '=' : ' ');
        sb.append(']');
        return sb.toString();
    }
    public void draw(WorldState w){
        float phi = w.getPhi();
        float S = w.getEntropy();
        float lam = w.getLambdaCoupling();
        float R = w.getR();
        String bPhi = bar(phi, 0f, 2f, 24);
        String bS   = bar(S,   0f,10f, 24);
        String bR   = bar(R,   0f, 2f, 24);
        System.out.printf("[HUD] Φ=%5.2f %s  S=%5.2f %s  λ=%4.2f  R=%5.2f %s%n", phi, bPhi, S, bS, lam, R, bR);
    }
}
