package com.stargen.graphics;

import com.stargen.math.Vector3D;
import com.stargen.engine.simulation.WorldState;
import com.stargen.research.TechScreen;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.GL;
import org.lwjgl.opengl.GL11;
import org.lwjgl.system.MemoryUtil;

import java.util.List;

public class LWJGLRenderer implements RendererBackend {
    private long window = 0;
    private int width = 960, height = 600;
    private boolean init = false;
    private WorldState world = null;
    private TechScreen techScreen = null;

    public void setWorld(WorldState w){ this.world = w; }
    public void setTechScreen(TechScreen t){ this.techScreen = t; }

    @Override
    public void init(){
        if (!GLFW.glfwInit()){
            System.err.println("[LWJGLRenderer] GLFW init failed; falling back to console.");
            return;
        }
        GLFW.glfwWindowHint(GLFW.GLFW_RESIZABLE, GLFW.GLFW_TRUE);
        window = GLFW.glfwCreateWindow(width, height, "StarGen — LWJGL", MemoryUtil.NULL, MemoryUtil.NULL);
        if (window == 0){
            System.err.println("[LWJGLRenderer] Window creation failed; fallback.");
            GLFW.glfwTerminate();
            return;
        }
        GLFW.glfwMakeContextCurrent(window);
        GL.createCapabilities();
        GLFW.glfwSwapInterval(1); // vsync
        init = true;
        System.out.println("[LWJGLRenderer] Initialized " + width + "x" + height);
    }

    private float hueShift = 0f;

    @Override
    public void setCamera(Vector3D pos, Vector3D euler){
        if (world != null){
            // RSVP coupling:
            float phi = world.getPhi();     // affects FOV-like zoom (we fake it via point size)
            float S   = world.getEntropy(); // jitter
            float lam = world.getLambdaCoupling(); // hue shift
            float R   = world.getR();       // brightness

            hueShift = lam; // cache for color modulation
            float pointSize = 1.5f + Math.min(6f, phi*2f);
            GL11.glPointSize(pointSize);
            float brightness = Math.max(0.2f, Math.min(1.0f, 0.5f + R*0.3f));
            float jitter = Math.min(0.5f, S * 0.03f);

            // Clear color maps lam & R; add entropy jitter to one channel
            GL11.glClearColor(0.05f + jitter, 0.05f + 0.2f*(lam%1f), 0.1f + 0.3f*brightness, 1.0f);
        } else {
            GL11.glClearColor(0.05f, 0.1f, 0.12f, 1.0f);
        }
    }

    @Override
    public void drawWorldTick(){
        if (!init) return;
        if (GLFW.glfwWindowShouldClose(window)){
            return;
        }
        GL11.glViewport(0, 0, width, height);
        GL11.glClear(GL11.GL_COLOR_BUFFER_BIT | GL11.GL_DEPTH_BUFFER_BIT);

        // Minimal starfield: draw pseudo-random points in NDC
        GL11.glBegin(GL11.GL_POINTS);
        for (int i=0;i<512;i++){
            float x = (float)Math.sin(i*12.9898 + hueShift)*43758.5453f;
            float y = (float)Math.cos(i*78.233  + hueShift)*12345.6789f;
            x = (x - (float)Math.floor(x))*2f - 1f;
            y = (y - (float)Math.floor(y))*2f - 1f;
            GL11.glVertex2f(x, y);
        }
        GL11.glEnd();

        // Handle tech overlay toggle and number hotkeys
        if (techScreen != null){
            if (GLFW.glfwGetKey(window, GLFW.GLFW_KEY_T) == GLFW.GLFW_PRESS){
                techScreen.visible = true;
            }
            if (techScreen.visible){
                // Draw translucent overlay background
                drawOverlayPanel(20, 20, width-40, height-40, 0f, 0f, 0f, 0.6f);
                // Render lines
                List<String> lines = techScreen.lines();
                int y = height - 60; // start near top
                for (String line: lines){
                    drawText(40, y, line, 2.0f);
                    y -= 18;
                }
                // Hotkeys 1..9
                for (int k=0;k<9;k++){
                    if (GLFW.glfwGetKey(window, GLFW.GLFW_KEY_1 + k) == GLFW.GLFW_PRESS){
                        techScreen.tryUnlockIndex(k+1);
                    }
                }
                if (GLFW.glfwGetKey(window, GLFW.GLFW_KEY_T) == GLFW.GLFW_RELEASE &&
                    GLFW.glfwGetKey(window, GLFW.GLFW_KEY_ESCAPE) == GLFW.GLFW_PRESS){
                    techScreen.visible = false;
                }
            }
        }

        GLFW.glfwSwapBuffers(window);
        GLFW.glfwPollEvents();
    }

    @Override
    public void shutdown(){
        if (window!=0){
            GLFW.glfwDestroyWindow(window);
            GLFW.glfwTerminate();
        }
        init = false;
    }

    public boolean isOpen(){
        return init && !GLFW.glfwWindowShouldClose(window);
    }

    // ---------- Simple overlay drawing ----------

    private void drawOverlayPanel(int x1,int y1,int x2,int y2,float r,float g,float b,float a){
        GL11.glMatrixMode(GL11.GL_PROJECTION);
        GL11.glPushMatrix();
        GL11.glLoadIdentity();
        GL11.glOrtho(0, width, 0, height, -1, 1);
        GL11.glMatrixMode(GL11.GL_MODELVIEW);
        GL11.glPushMatrix();
        GL11.glLoadIdentity();

        GL11.glDisable(GL11.GL_DEPTH_TEST);
        GL11.glColor4f(r,g,b,a);
        GL11.glBegin(GL11.GL_QUADS);
        GL11.glVertex2f(x1, y1);
        GL11.glVertex2f(x2, y1);
        GL11.glVertex2f(x2, y2);
        GL11.glVertex2f(x1, y2);
        GL11.glEnd();
        GL11.glEnable(GL11.GL_DEPTH_TEST);

        GL11.glPopMatrix();
        GL11.glMatrixMode(GL11.GL_PROJECTION);
        GL11.glPopMatrix();
        GL11.glMatrixMode(GL11.GL_MODELVIEW);
    }

    private static final String[] FONT5x7 = new String[]{
        "00000" ,"00000" ,"00000" ,"00000" ,"00000" ,"00000" ,"00000", // space 32
        // '!' to '/' omitted minimal; we support digits, letters, basic punctuation used
    };

    // Minimal glyphs for ASCII subset we need; if missing, render as spaces.
    private int[][] glyph(char c){
        // Hardcode digits 0-9 and some letters used in our tech names (coarse 5x7)
        switch (Character.toUpperCase(c)){
            case 'A': return new int[][]{
                {0,1,1,1,0},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,1,1,1,1},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,0,1}};
            case 'E': return new int[][]{
                {1,1,1,1,1},
                {1,0,0,0,0},
                {1,1,1,1,0},
                {1,0,0,0,0},
                {1,1,1,1,1},
                {1,0,0,0,0},
                {1,1,1,1,1}};
            case 'F': return new int[][]{
                {1,1,1,1,1},
                {1,0,0,0,0},
                {1,1,1,1,0},
                {1,0,0,0,0},
                {1,0,0,0,0},
                {1,0,0,0,0},
                {1,0,0,0,0}};
            case 'I': return new int[][]{
                {1,1,1,1,1},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {1,1,1,1,1}};
            case 'N': return new int[][]{
                {1,0,0,0,1},
                {1,1,0,0,1},
                {1,0,1,0,1},
                {1,0,0,1,1},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,0,1}};
            case 'O': return new int[][]{
                {0,1,1,1,0},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {0,1,1,1,0}};
            case 'Q': return new int[][]{
                {0,1,1,1,0},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,1,0},
                {1,0,0,0,1},
                {0,1,1,0,1}};
            case 'R': return new int[][]{
                {1,1,1,1,0},
                {1,0,0,0,1},
                {1,1,1,1,0},
                {1,0,1,0,0},
                {1,0,0,1,0},
                {1,0,0,0,1},
                {1,0,0,0,1}};
            case 'S': return new int[][]{
                {0,1,1,1,1},
                {1,0,0,0,0},
                {0,1,1,1,0},
                {0,0,0,0,1},
                {1,1,1,1,0},
                {0,0,0,0,1},
                {1,1,1,1,0}};
            case 'T': return new int[][]{
                {1,1,1,1,1},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {0,0,1,0,0}};
            case 'U': return new int[][]{
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {1,0,0,0,1},
                {0,1,1,1,0}};
            case 'Y': return new int[][]{
                {1,0,0,0,1},
                {0,1,0,1,0},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {0,0,1,0,0},
                {0,0,1,0,0}};
            case ' ': return new int[][]{
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,0,0,0,0}};
            case '-': return new int[][]{
                {0,0,0,0,0},
                {0,0,0,0,0},
                {1,1,1,1,1},
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,0,0,0,0}};
            case '.': return new int[][]{
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,0,0,0,0},
                {0,1,1,0,0},
                {0,1,1,0,0}};
            default:
                if (c>='0' && c<='9'){
                    // crude digits
                    int d = c - '0';
                    int[][][] DIG = new int[][][]{
                        {{0,1,1,1,0},{1,0,0,0,1},{1,0,0,1,1},{1,0,1,0,1},{1,1,0,0,1},{1,0,0,0,1},{0,1,1,1,0}}, //0
                        {{0,0,1,0,0},{0,1,1,0,0},{1,0,1,0,0},{0,0,1,0,0},{0,0,1,0,0},{0,0,1,0,0},{1,1,1,1,1}}, //1
                        {{0,1,1,1,0},{1,0,0,0,1},{0,0,0,0,1},{0,0,0,1,0},{0,0,1,0,0},{0,1,0,0,0},{1,1,1,1,1}}, //2
                        {{1,1,1,1,0},{0,0,0,0,1},{0,0,1,1,0},{0,0,0,0,1},{0,0,0,0,1},{1,0,0,0,1},{0,1,1,1,0}}, //3
                        {{0,0,0,1,0},{0,0,1,1,0},{0,1,0,1,0},{1,0,0,1,0},{1,1,1,1,1},{0,0,0,1,0},{0,0,0,1,0}}, //4
                        {{1,1,1,1,1},{1,0,0,0,0},{1,1,1,1,0},{0,0,0,0,1},{0,0,0,0,1},{1,0,0,0,1},{0,1,1,1,0}}, //5
                        {{0,1,1,1,0},{1,0,0,0,1},{1,0,0,0,0},{1,1,1,1,0},{1,0,0,0,1},{1,0,0,0,1},{0,1,1,1,0}}, //6
                        {{1,1,1,1,1},{0,0,0,0,1},{0,0,0,1,0},{0,0,1,0,0},{0,1,0,0,0},{0,1,0,0,0},{0,1,0,0,0}}, //7
                        {{0,1,1,1,0},{1,0,0,0,1},{1,0,0,0,1},{0,1,1,1,0},{1,0,0,0,1},{1,0,0,0,1},{0,1,1,1,0}}, //8
                        {{0,1,1,1,0},{1,0,0,0,1},{1,0,0,0,1},{0,1,1,1,1},{0,0,0,0,1},{1,0,0,0,1},{0,1,1,1,0}}  //9
                    };
                    return DIG[d];
                }
                return new int[][]{
                    {0,0,0,0,0},
                    {0,0,0,0,0},
                    {0,0,0,0,0},
                    {0,0,0,0,0},
                    {0,0,0,0,0},
                    {0,0,0,0,0},
                    {0,0,0,0,0}};
        }
    }

    private void drawText(int x, int y, String text, double scale){
        GL11.glMatrixMode(GL11.GL_PROJECTION);
        GL11.glPushMatrix();
        GL11.glLoadIdentity();
        GL11.glOrtho(0, width, 0, height, -1, 1);
        GL11.glMatrixMode(GL11.GL_MODELVIEW);
        GL11.glPushMatrix();
        GL11.glLoadIdentity();

        GL11.glDisable(GL11.GL_DEPTH_TEST);
        GL11.glColor4f(0.8f, 0.95f, 1.0f, 1.0f);
        int cursorX = x;
        for (int i=0;i<text.length();i++){
            int[][] g = glyph(text.charAt(i));
            int gw = 5, gh = 7;
            int px = cursorX;
            for (int gy=0; gy<gh; gy++){
                for (int gx=0; gx<gw; gx++){
                    if (g[gy][gx] == 1){
                        int sx = (int)(px + gx*scale);
                        int sy = (int)(y + (gh-1-gy)*scale);
                        int s = (int)scale;
                        GL11.glBegin(GL11.GL_QUADS);
                        GL11.glVertex2f(sx,   sy);
                        GL11.glVertex2f(sx+s, sy);
                        GL11.glVertex2f(sx+s, sy+s);
                        GL11.glVertex2f(sx,   sy+s);
                        GL11.glEnd();
                    }
                }
            }
            cursorX += (int)(gw*scale + 2);
        }
        GL11.glEnable(GL11.GL_DEPTH_TEST);

        GL11.glPopMatrix();
        GL11.glMatrixMode(GL11.GL_PROJECTION);
        GL11.glPopMatrix();
        GL11.glMatrixMode(GL11.GL_MODELVIEW);
    }
}
