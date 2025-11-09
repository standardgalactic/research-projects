package com.stargen.missions;

import java.io.IOException;
import java.nio.file.*;
import java.util.*;
import com.stargen.world.GalaxyMap;

public class MissionFactory {
    public static ScriptMission fromFile(GalaxyMap galaxy, Path p) throws IOException {
        Map<String,String> cfg = MissionDSL.parse(p);
        return new ScriptMission(galaxy, cfg);
        }
    public static ScriptMission proceduralEntropyStabilize(GalaxyMap galaxy, int nodeIndex, float duration, float entropyDeltaPerSec){
        Map<String,String> cfg = new HashMap<>();
        cfg.put("type","STABILIZE_NODE");
        cfg.put("node", String.valueOf(nodeIndex));
        cfg.put("duration", String.valueOf(duration));
        cfg.put("effect", "entropy:" + entropyDeltaPerSec);
        return new ScriptMission(galaxy, cfg);
    }
}
