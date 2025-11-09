package com.stargen.graphics;

import com.stargen.math.Vector3D;

public class LegacyRenderer implements RendererBackend {
    @Override public void init(){ /* no window */ }
    @Override public boolean isOpen(){ return true; }
    @Override public void setCamera(Vector3D pos, Vector3D euler){ /* noop */ }
    @Override public void drawWorldTick(){ /* noop */ }
    @Override public void shutdown(){ /* noop */ }
}
