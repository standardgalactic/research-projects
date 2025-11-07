package com.stargen.research;

public class Technology {
    public final String name;
    public final float dPhi;
    public final float dS;
    public final float dLambda;
    public boolean unlocked = false;

    public Technology(String name, float dPhi, float dS, float dLambda){
        this.name = name; this.dPhi = dPhi; this.dS = dS; this.dLambda = dLambda;
    }
}
