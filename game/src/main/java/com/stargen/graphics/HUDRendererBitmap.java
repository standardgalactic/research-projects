package com.stargen.graphics;
import com.stargen.engine.simulation.WorldState;

public class HUDRendererBitmap implements HUDRenderer {
    @Override public void draw(WorldState w, int width, int height){
        // Minimal placeholder; in v11 we printed to console; window overlay handled by NanoVG or renderer text.
        // Keep empty to avoid GL text boilerplate.
    }
}
