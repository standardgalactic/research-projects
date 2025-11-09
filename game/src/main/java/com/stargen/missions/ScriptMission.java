package com.stargen.missions;

import java.util.Map;
import com.stargen.world.GalaxyMap;
import com.stargen.world.StarSystem;

public class ScriptMission {
    private final String type;
    private final int node;
    private final float duration;
    private float timer = 0f;
    private final String effect; // e.g., "entropy:-0.02"

    private final GalaxyMap galaxy;

    public ScriptMission(GalaxyMap galaxy, Map<String,String> cfg){
        this.galaxy = galaxy;
        this.type = cfg.getOrDefault("type", "STABILIZE_NODE");
        this.node = Integer.parseInt(cfg.getOrDefault("node", "0"));
        this.duration = Float.parseFloat(cfg.getOrDefault("duration", "60"));
        this.effect = cfg.getOrDefault("effect", "entropy:-0.01");
    }

    public void tick(float dt){
        timer += dt;
        if ("STABILIZE_NODE".equals(type)){
            StarSystem s = galaxy.get(node);
            if (effect.startsWith("entropy:")){
                float v = Float.parseFloat(effect.substring("entropy:".length()));
                s.entropy = Math.max(0f, s.entropy + v * dt);
            }
        }
        if (timer >= duration){
            // mission complete — in a real engine, emit event
        }
    }
}
