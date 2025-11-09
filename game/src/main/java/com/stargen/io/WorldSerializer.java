package com.stargen.io;

import java.util.*;
import java.nio.file.*;
import java.io.IOException;
import com.stargen.engine.simulation.WorldState;
import com.stargen.research.TechTree;
import com.stargen.research.Technology;

public class WorldSerializer {
    public static void save(Path path, WorldState world, TechTree techs) throws IOException {
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        sb.append(String.format("  \"phi\": %.5f,\n", world.getPhi()));
        sb.append(String.format("  \"entropy\": %.5f,\n", world.getEntropy()));
        sb.append(String.format("  \"lambda\": %.5f,\n", world.getLambdaCoupling()));
        sb.append("  \"unlocked\": [");
        boolean first = true;
        for (Technology t : techs.list()){
            if (t.unlocked){
                if (!first) sb.append(", ");
                sb.append("\"").append(t.name.replace(""","\\"))
                  .append("\"");
                first = false;
            }
        }
        sb.append("]\n}");
        Files.writeString(path, sb.toString());
    }
}
