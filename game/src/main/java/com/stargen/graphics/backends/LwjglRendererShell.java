package com.stargen.graphics.backends;

/**
 * Placeholder LWJGL renderer shell.
 * Swap in LWJGL init loop and OpenGL calls.
 * This file compiles without LWJGL; no imports to external libs.
 */
public class LwjglRendererShell {
    public void init(){
        System.out.println("[LWJGL] init placeholder");
    }
    public void drawFrame(){
        // TODO: real GL calls here
    }
    public void shutdown(){
        System.out.println("[LWJGL] shutdown");
    }
}
