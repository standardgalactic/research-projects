package com.stargen.engine;

import com.stargen.engine.simulation.WorldState;
import com.stargen.entities.PlayerShip;
import com.stargen.entities.ai.AIPathFollower;
import com.stargen.controls.InputHandler;
import com.stargen.graphics.HUDRenderer;
import com.stargen.graphics.RendererBackend;
import com.stargen.graphics.LWJGLRenderer;
import com.stargen.world.NavMesh;
import com.stargen.world.TunnelLevel;
import com.stargen.math.Vector3D;
import com.stargen.io.LevelLoader;
import com.stargen.research.*;

public class GameLoop {

    private WorldState world;
    private PlayerShip player;
    private InputHandler input;
    private boolean isRunning = true;

    // Demo scene
    private HUDRenderer hud = new HUDRenderer();
    private AIPathFollower follower;
    private NavMesh nav;
    private float hudTimer = 0f;
    private RendererBackend renderer = null;
    private TechLogic techLogic = new TechLogic();
    private TechTree techTree = new TechTree();
    private TechScreen techScreen;

    public GameLoop(){
        // RSVP world
        this.world = new WorldState(1.0f, 0.2f, 0.4f);

        // Player
        this.player = new PlayerShip(new Vector3D(0,0,0), world);
        this.input = new InputHandler(player);

        // Level load from assets (falls back to empty if error)
        try {
            LevelLoader.Result res = LevelLoader.load("assets/levels/level1.txt");
            this.nav = NavMesh.fromTunnel(res.level);
            // pick closest nodes to S and G by index heuristic
            int startNode = 0;
            int goalNode = Math.max(0, nav.nodes.size()-1);
            this.follower = new AIPathFollower(new Vector3D(res.sx, res.sy, res.sz), nav);
            this.follower.follow(startNode, goalNode);
        } catch (Exception ex){
            System.out.println("[GameLoop] Level load failed, using empty grid. " + ex);
            TunnelLevel lvl = new TunnelLevel(10, 6, 10); // empty
            for (int x=0;x<lvl.W;x++)
                for (int y=0;y<lvl.H;y++)
                    for (int z=0;z<lvl.D;z++)
                        lvl.solid[x][y][z] = false;
            this.nav = NavMesh.fromTunnel(lvl);
            this.follower = new AIPathFollower(new Vector3D(1,1,1), nav);
            int startNode = 0;
            int goalNode = Math.max(0, nav.nodes.size()-1);
            this.follower.follow(startNode, goalNode);
        }

        // Tech screen
        this.techScreen = new TechScreen(techLogic, techTree, world);

        // Optional LWJGL renderer
        if ("lwjgl".equalsIgnoreCase(System.getProperty("renderer", ""))){
            LWJGLRenderer l = new LWJGLRenderer();
            l.init();
            l.setWorld(world);
            l.setTechScreen(techScreen);
            renderer = l;
        }

        System.out.println("[GameLoop] Demo initialized: NavMesh nodes=" + nav.nodes.size());
    }

    public void run(){
        long last = System.nanoTime();
        while (isRunning){
            long now = System.nanoTime();
            float dt = (now - last) / 1_000_000_000.0f;
            last = now;

            // Input and physics
            input.processInput(dt);
            player.update(dt);
            follower.update(dt);

            // RSVP world tick
            world.tick(dt);

            // Periodic HUD (once per ~1s)
            hudTimer += dt;
            if (hudTimer >= 1.0f){
                hud.draw(world);
                hudTimer = 0f;
            }

            if (renderer != null){
                renderer.setCamera(player.getPosition(), player.getOrientation());
                renderer.drawWorldTick();
            }

            try { Thread.sleep(16); } catch(InterruptedException ie){ Thread.currentThread().interrupt(); }
        }
        if (renderer != null) renderer.shutdown();
    }

    public static void main(String[] args){
        new GameLoop().run();
    }
}
