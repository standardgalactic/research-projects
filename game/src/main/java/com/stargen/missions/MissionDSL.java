package com.stargen.missions;

import java.util.*;
import java.nio.file.*;
import java.io.IOException;

public class MissionDSL {
    public static Map<String,String> parse(Path p) throws IOException {
        List<String> lines = Files.readAllLines(p);
        Map<String,String> map = new HashMap<>();
        for (String raw : lines){
            String line = raw.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            int eq = line.indexOf('=');
            if (eq < 0) continue;
            String k = line.substring(0, eq).trim();
            String v = line.substring(eq+1).trim();
            map.put(k, v);
        }
        return map;
    }
}
