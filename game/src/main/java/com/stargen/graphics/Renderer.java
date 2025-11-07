package com.stargen.graphics;

import com.stargen.entities.PlayerShip;
import com.stargen.math.Vector3D;

public class Renderer {
    private final String WINDOW_TITLE;
    private final int WIDTH;
    private final int HEIGHT;
    private final float FOV;

    public Renderer(int width, int height){
        this.WINDOW_TITLE = "StarGen 6DOF Shooter";
        this.WIDTH = width; this.HEIGHT = height;
        this.FOV = 60.0f;
        System.out.println("Renderer init: " + WIDTH + "x" + HEIGHT + " FOV=" + FOV);
    }

    public void setupCamera(Vector3D position, Vector3D orientation){
        // Placeholder for real 3D math
    }

    public void renderScene(PlayerShip player){
        setupCamera(player.getPosition(), player.getOrientation());
        // Placeholder draw calls
        if ((int)(System.nanoTime()%120)==0)
            System.out.println("Render @ " + player.getPosition());
    }
}
