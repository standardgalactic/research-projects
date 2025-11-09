package com.stargen.graphics;
import com.stargen.engine.simulation.WorldState;

public class HUDRendererNanoVG implements HUDRenderer {
    private final NanoVGOverlay nvg = new NanoVGOverlay();
    private boolean tried=false;
    private void ensureInit(){
        if (!tried){ nvg.init(); tried=true; }
    }
    @Override public void draw(WorldState w, int width, int height){
        ensureInit();
        if (!nvg.available()) return;
        nvg.begin(width, height);
        nvg.panel(12, height-80, 420, 60);
        String line = String.format("Φ=%5.2f  S=%5.2f  λ=%4.2f  R=%5.2f", w.getPhi(), w.getEntropy(), w.getLambdaCoupling(), w.getR());
        nvg.text(24, height-45, line);
        nvg.end();
    }
}
