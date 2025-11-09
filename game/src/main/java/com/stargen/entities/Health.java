package com.stargen.entities;
public class Health {
    private float hp, max;
    public Health(float max){ this.max=max; this.hp=max; }
    public void damage(float d){ hp -= d; if (hp<0) hp=0; }
    public boolean dead(){ return hp<=0; }
    public float hp(){ return hp; }
}
