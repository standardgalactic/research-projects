package com.stargen.research;

import java.util.*;
import com.stargen.engine.simulation.WorldState;

public class TechScreen {
    public boolean visible = false;
    private final TechLogic logic;
    private final TechTree tree;
    private final WorldState world;

    public TechScreen(TechLogic logic, TechTree tree, WorldState world){
        this.logic = logic;
        this.tree = tree;
        this.world = world;
    }

    public List<String> lines(){
        List<String> out = new ArrayList<>();
        out.add("=== TECHNOLOGY === (Press T to close; 1-9 to unlock)");
        Set<String> unlocked = new HashSet<>();
        for (Technology t: tree.techs) if (t.unlocked) unlocked.add(t.name);
        int idx = 1;
        for (Technology t: tree.techs){
            boolean can = logic.canUnlock(t.name, unlocked);
            String mark = t.unlocked ? "[✓]" : (can ? "[>]" : "[ ]");
            out.add(String.format("%d) %s %-30s  tier=%d  prereqs=%s  Δ(Φ,S,λ)=(%.2f,%.2f,%.2f)",
                idx, mark, t.name, logic.tierOf(t.name), String.join("+", logic.prereqsOf(t.name)),
                t.dPhi, t.dS, t.dLambda));
            idx++;
            if (idx>9) break;
        }
        return out;
    }

    public void tryUnlockIndex(int oneBased){
        if (oneBased < 1) return;
        int idx = 1;
        for (Technology t: tree.techs){
            if (idx == oneBased){
                // delegate to tree; TechTree enforces prereqs and applies deltas
                tree.unlock(t.name);
                return;
            }
            idx++;
        }
    }
}
