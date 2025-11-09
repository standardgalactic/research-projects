package com.stargen.graphics;

import com.stargen.math.Vector3D;

/** Default dependency-free backend that prints telemetry instead of drawing. */
public class StubRenderer implements RendererBackend {
    @Override public void init(){ System.out.println("[Renderer] init stub"); }
    @Override public void setCamera(Vector3D pos, Vector3D euler){ /* no-op */ }
    @Override public void drawWorldTick(){ /* no-op */ }
    @Override public void shutdown(){ System.out.println("[Renderer] shutdown stub"); }
}
