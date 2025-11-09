package com.stargen.research;

import java.util.stream.*;

import java.util.*;
import com.stargen.engine.simulation.WorldState;

public class TechUI {
    private final TechTree tree;
    private final TechLogic logic = new TechLogic();
    private final Map<Integer, Technology> indexMap = new LinkedHashMap<>();

    public TechUI(TechTree tree){
        this.tree = tree;
        rebuild();
    }

    public void rebuild(){
        indexMap.clear();
        int i = 1;
        for (Technology t : tree.list()){
            indexMap.put(i++, t);
        }
    }

    public void printMenu(){
        System.out.println("-- Techs --");
        for (Map.Entry<Integer, Technology> e : indexMap.entrySet()){
            Technology t = e.getValue();
            System.out.printf("[%d] %s %s (tier %d, %s) dPhi=%.2f dS=%.2f dLambda=%.2f%n",
                e.getKey(), t.name, (t.unlocked?"[UNLOCKED]":""), getTier(t), getBranch(t), t.dPhi, t.dS, t.dLambda);
        }
        System.out.println("Press 1-9 to unlock matching tech index (if available).");
    }

    public void unlockByIndex(int idx){
        // enforce prereqs via TechLogic
        Technology t = indexMap.get(idx);
        if (t == null){
            System.out.println("No tech bound to index " + idx);
            return;
        }
        Set<String> unlocked = tree.list().stream().filter(tt->tt.unlocked).map(tt->tt.name).collect(Collectors.toSet());
        if (logic.canUnlock(t.name, unlocked)) tree.unlock(t.name); else System.out.println("[TechUI] Prerequisites not met for: " + t.name);
    }

    // These are comments-only metadata in generated TechTree; derive via name tags in practice.
    private int getTier(Technology t){ return extractTierFromName(t.name); }
    private String getBranch(Technology t){ return extractBranchFromName(t.name); }

    private int extractTierFromName(String n){ return 1; } // placeholder
    private String extractBranchFromName(String n){ return "mixed"; } // placeholder
}
