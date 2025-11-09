package com.stargen.graphics.backends;

/**
 * Placeholder jMonkeyEngine renderer shell.
 * Implement Application subclass and attach states for real usage.
 * Kept dependency-free here.
 */
public class JmeRendererShell {
    public void init(){
        System.out.println("[JME] init placeholder");
    }
    public void drawFrame(){
        // TODO: real JME update/render
    }
    public void shutdown(){
        System.out.println("[JME] shutdown");
    }
}
