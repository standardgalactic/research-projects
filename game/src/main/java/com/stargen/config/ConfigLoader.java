package com.stargen.config;

import java.io.IOException;
import java.nio.file.*;
import java.util.Properties;

public class ConfigLoader {
    private final Properties p = new Properties();
    public ConfigLoader(){
        Path cfg = Paths.get("config/game.properties");
        if (Files.exists(cfg)){
            try { p.load(Files.newBufferedReader(cfg)); } catch (IOException ignored){}
        }
    }
    public float f(String key, float def){
        String v = p.getProperty(key);
        if (v==null) return def;
        try { return Float.parseFloat(v.trim()); } catch(Exception e){ return def;}
    }
    public String s(String key, String def){ String v=p.getProperty(key); return v==null?def:v; }
}
