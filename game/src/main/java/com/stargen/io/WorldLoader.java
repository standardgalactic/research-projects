package com.stargen.io;

import java.nio.file.*;
import java.io.IOException;
import java.util.*;
import com.stargen.engine.simulation.WorldState;
import com.stargen.research.TechTree;
import com.stargen.research.Technology;
import com.fasterxml.jackson.databind.ObjectMapper;

public class WorldLoader {
    public static void load(Path path, WorldState world, TechTree techs) throws IOException {
        ObjectMapper om = new ObjectMapper();
        Map<?,?> m = om.readValue(Files.readString(path), Map.class);
        Number phi = (Number)m.getOrDefault("phi", 1.0);
        Number ent = (Number)m.getOrDefault("entropy", 0.2);
        Number lam = (Number)m.getOrDefault("lambda", 0.4);
        world.addPhi(phi.floatValue() - world.getPhi());
        world.addEntropy(ent.floatValue() - world.getEntropy());
        world.adjustLambda(lam.floatValue() - world.getLambdaCoupling());

        List<?> unlocked = (List<?>) m.getOrDefault("unlocked", List.of());
        for (Object o : unlocked){
            String name = String.valueOf(o);
            for (Technology t : techs.list()){
                if (t.name.equals(name)) t.unlocked = true;
            }
        }
    }
}
