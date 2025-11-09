package com.stargen.graphics;

import java.lang.reflect.*;

public class NanoVGOverlay {
    private Object vg=null;
    private boolean available=false;
    private Method nvgCreate, nvgBeginFrame, nvgEndFrame, nvgBeginPath, nvgRect, nvgFillColor, nvgFill, nvgText;
    private Class<?> NVG, NVGColor;

    public void init(){
        try {
            NVG = Class.forName("org.lwjgl.nanovg.NanoVG");
            NVGColor = Class.forName("org.lwjgl.nanovg.NVGColor");
            nvgCreate    = NVG.getMethod("nvgCreate", int.class);
            nvgBeginFrame= NVG.getMethod("nvgBeginFrame", long.class, int.class, int.class, float.class);
            nvgEndFrame  = NVG.getMethod("nvgEndFrame", long.class);
            nvgBeginPath = NVG.getMethod("nvgBeginPath", long.class);
            nvgRect      = NVG.getMethod("nvgRect", long.class, float.class, float.class, float.class, float.class);
            nvgFillColor = NVG.getMethod("nvgFillColor", long.class, NVGColor);
            nvgFill      = NVG.getMethod("nvgFill", long.class);
            nvgText      = NVG.getMethod("nvgText", long.class, float.class, float.class, CharSequence.class);
            vg = nvgCreate.invoke(null, 1|2);
            available = vg != null;
        } catch (Throwable t){ available=false; }
    }
    public boolean available(){ return available; }
    public void begin(int w,int h){
        if (!available) return;
        try { nvgBeginFrame.invoke(null, ((Number)vg).longValue(), w, h, 1.0f); } catch(Throwable ignore){}
    }
    public void end(){
        if (!available) return;
        try { nvgEndFrame.invoke(null, ((Number)vg).longValue()); } catch(Throwable ignore){}
    }
    public void panel(float x,float y,float w,float h){
        if (!available) return;
        try {
            long ctx=((Number)vg).longValue();
            Object color = NVGColor.getMethod("create").invoke(null);
            NVGColor.getMethod("r", NVGColor, float.class).invoke(null, color, 0f);
            NVGColor.getMethod("g", NVGColor, float.class).invoke(null, color, 0f);
            NVGColor.getMethod("b", NVGColor, float.class).invoke(null, color, 0f);
            NVGColor.getMethod("a", NVGColor, float.class).invoke(null, color, 0.55f);
            nvgBeginPath.invoke(null, ctx); nvgRect.invoke(null, ctx, x, y, w, h); nvgFillColor.invoke(null, ctx, color); nvgFill.invoke(null, ctx);
        } catch(Throwable ignore){}
    }
    public void text(float x,float y,String s){
        if (!available) return;
        try { nvgText.invoke(null, ((Number)vg).longValue(), x, y, s); } catch(Throwable ignore){}
    }
}
