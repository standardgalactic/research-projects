package com.stargen.engine;

import java.util.ArrayList;
import java.util.List;

import com.stargen.engine.simulation.WorldState;
import com.stargen.entities.PlayerShip;
import com.stargen.entities.ai.AIController;
import com.stargen.entities.weapons.Projectile;
import com.stargen.graphics.Renderer;
import com.stargen.graphics.HUDRenderer;
import com.stargen.controls.InputHandler;
import com.stargen.math.Vector3D;
import com.stargen.research.TechTree;
import com.stargen.world.GalaxyMap;
import com.stargen.missions.Mission;

public class GameLoop {

    private PlayerShip playerShip;
    private final List<Object> entities = new ArrayList<>(); // simple heterogeneous list for demo
    private InputHandler inputHandler;
    private Renderer renderer;
    private HUDRenderer hud;
    private WorldState world;
    private TechTree techTree;
    private GalaxyMap galaxy;
    private Mission currentMission;

    private boolean isRunning;
    private final static float TARGET_FPS = 60.0f;
    private final static long TARGET_FRAME_TIME_NANO = (long)(1_000_000_000L / TARGET_FPS);
    private long frameCount = 0;

    public GameLoop(){
        // World & research
        this.world = new WorldState(1.0f, 0.2f, 0.4f);
        this.techTree = new TechTree(world);

        // Player
        Vector3D start = new Vector3D(0,0,0);
        this.playerShip = new PlayerShip(start, 50.0f, 2.0f);
        this.inputHandler = new InputHandler(playerShip);

        // AI
        AIController ai1 = new AIController(new Vector3D(100,10,-50), playerShip);
        entities.add(ai1);

        // Galaxy & mission
        this.galaxy = new GalaxyMap(8, world);
        this.currentMission = Mission.stabilizeNode(galaxy, 0);

        // Rendering
        this.renderer = new Renderer(960, 540);
        this.hud = new HUDRenderer();

        this.isRunning = true;

        System.out.println("StarGen initialized.");
    }

    private void applyRSVPFlightCoupling(){
        // Increase handling instability as entropy rises (S ↑ => wobble ↑, thrust ↓)
        float S = world.getEntropy();
        float phi = world.getPhi();
        float wobble = Math.min(0.6f, 0.05f * S);
        float thrustScale = Math.max(0.5f, 1.0f - 0.03f * S) * (0.8f + 0.02f * phi);
        playerShip.setHandling(wobble, thrustScale);
    }

    public void run(){
        long last = System.nanoTime();
        while (isRunning) {
            long now = System.nanoTime();
            float dt = (now - last) / 1e9f;
            last = now;
            frameCount++;

            // 1) World RSVP tick
            world.tick(dt);
            applyRSVPFlightCoupling();

            // 2) Input & updates
            inputHandler.processInput(dt);
            playerShip.update(dt);
            for (Object o : entities) {
                if (o instanceof AIController) ((AIController)o).update(dt);
                if (o instanceof Projectile) ((Projectile)o).update(dt);
            }

            // 3) Mission hook (affects world or nodes)
            if (currentMission != null) currentMission.tick(dt);

            // 4) Render & HUD
            renderer.renderScene(playerShip);
            hud.drawTelemetry(world, playerShip);

            // 5) Demo: occasionally unlock a tech
            if (frameCount == 600) techTree.unlock("Efficient Supply Routing");
            if (frameCount == 1200) techTree.unlock("Constitutional Safety Layer");

            // 6) sleep to target FPS
            long sleepMs = (TARGET_FRAME_TIME_NANO - (System.nanoTime() - now)) / 1_000_000;
            if (sleepMs > 0){
                try { Thread.sleep(sleepMs); } catch (InterruptedException e){ Thread.currentThread().interrupt(); }
            }
            if (frameCount > 1800) isRunning = false; // auto-exit demo
        }
    }

    public static void main(String[] args){
        new GameLoop().run();
    }
}
