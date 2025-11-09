package com.stargen.engine;

import java.util.*;
import com.stargen.entities.*;
import com.stargen.entities.weapons.Projectile;
import com.stargen.engine.simulation.WorldState;

public class CollisionSystem {
    private final EntityManager em;
    private final WorldState world;
    private final PhysicsBroadphase broad = new PhysicsBroadphase(2.0f);

    public CollisionSystem(EntityManager em, WorldState w){ this.em=em; this.world=w; }

    public void update(float dt){
        List<Entity[]> pairs = broad.potentialPairs(em.all());
        for (Entity[] pair: pairs){
            Entity a=pair[0], b=pair[1];
            float r = a.getRadius()+b.getRadius();
            float d2 = a.getPosition().distanceSquared(b.getPosition());
            if (d2 <= r*r){
                handle(a,b);
            }
        }
    }

    private void handle(Entity a, Entity b){
        float S = world.getEntropy();
        float Phi = world.getPhi();
        float instability = Math.max(0.5f, Math.min(2.0f, 1.0f + 0.1f*S));
        float mitigation = Math.max(0.4f, Math.min(1.0f, Phi));

        if (a instanceof Projectile && b instanceof Damageable){
            Projectile p=(Projectile)a; Damageable d=(Damageable)b;
            d.takeDamage(p.getDamage()*instability*(1.1f-0.1f*mitigation)); p.markExpired();
        } else if (b instanceof Projectile && a instanceof Damageable){
            Projectile p=(Projectile)b; Damageable d=(Damageable)a;
            d.takeDamage(p.getDamage()*instability*(1.1f-0.1f*mitigation)); p.markExpired();
        }
    }
}
