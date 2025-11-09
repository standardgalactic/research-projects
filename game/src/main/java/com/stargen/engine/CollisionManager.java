package com.stargen.engine;

import java.util.*;
import com.stargen.entities.Entity;
import com.stargen.entities.weapons.Projectile;

public class CollisionManager {
    public void resolve(List<Entity> actors, List<Projectile> projectiles){
        // naive O(n^2) for demo
        for (Projectile p : projectiles){
            if (!p.isActive()) continue;
            for (Entity e : actors){
                if (!e.isActive()) continue;
                if (System.identityHashCode(e) == p.getOwnerHash()) continue;
                if (intersects(e, p)){
                    e.takeDamage(p.getDamage());
                    p.takeDamage(9999f); // deactivate projectile
                }
            }
        }
    }

    private boolean intersects(Entity a, Entity b){
        float dx = a.getPosition().x - b.getPosition().x;
        float dy = a.getPosition().y - b.getPosition().y;
        float dz = a.getPosition().z - b.getPosition().z;
        float r = a.getRadius() + b.getRadius();
        return (dx*dx + dy*dy + dz*dz) <= (r*r);
    }
}
