package com.stargen.research;

import java.nio.file.*;
import java.io.IOException;
import java.util.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;

public class TechLogic {
    public static class TechMeta {
        public String name;
        public int tier;
        public String branch;
        public List<String> prereqs = new ArrayList<>();
        public float dPhi, dS, dLambda;
    }

    private final Map<String, TechMeta> byName = new HashMap<>();

    public TechLogic(){
        try {
            Path p = Paths.get("research.techs.json");
            if (Files.exists(p)){
                ObjectMapper om = new ObjectMapper();
                Map<String, Object> root = om.readValue(Files.readString(p), new TypeReference<Map<String,Object>>(){});
                List<Map<String,Object>> techs = (List<Map<String,Object>>) root.getOrDefault("techs", List.of());
                for (Map<String,Object> m : techs){
                    TechMeta t = new TechMeta();
                    t.name = String.valueOf(m.get("name"));
                    t.tier = ((Number)m.getOrDefault("tier", 1)).intValue();
                    t.branch = String.valueOf(m.getOrDefault("branch", "mixed"));
                    Object pr = m.get("prereqs");
                    if (pr instanceof List<?>){
                        for (Object o : (List<?>)pr) t.prereqs.add(String.valueOf(o));
                    }
                    t.dPhi = ((Number)m.getOrDefault("dPhi", 0)).floatValue();
                    t.dS = ((Number)m.getOrDefault("dS", 0)).floatValue();
                    t.dLambda = ((Number)m.getOrDefault("dLambda", 0)).floatValue();
                    byName.put(t.name, t);
                }
            }
        } catch (IOException e){
            System.err.println("[TechLogic] failed to load research.techs.json: " + e.getMessage());
        }
    }

    public boolean canUnlock(String techName, Set<String> unlocked){
        TechMeta t = byName.get(techName);
        if (t == null) return true; // allow unknowns
        for (String pre : t.prereqs){
            if (!unlocked.contains(pre)) return false;
        }
        return true;
    }

    public Optional<TechMeta> meta(String name){
        return Optional.ofNullable(byName.get(name));
    }
}
