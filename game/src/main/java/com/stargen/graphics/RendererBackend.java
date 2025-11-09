package com.stargen.graphics;

import com.stargen.math.Vector3D;

public interface RendererBackend {
    void init();
    void setCamera(Vector3D position, Vector3D euler);
    void drawWorldTick();
    void shutdown();
}
