package com.stargen.engine;

import java.util.*;
import com.stargen.entities.Entity;

public class PhysicsBroadphase {
    private final float cellSize;
    public PhysicsBroadphase(float cell){ this.cellSize=cell; }

    private static final class CellKey {
        final int x,y,z;
        CellKey(int x,int y,int z){ this.x=x; this.y=y; this.z=z; }
        @Override public int hashCode(){ return (x*73856093) ^ (y*19349663) ^ (z*83492791); }
        @Override public boolean equals(Object o){
            if(!(o instanceof CellKey)) return false;
            CellKey k=(CellKey)o; return x==k.x && y==k.y && z==k.z;
        }
    }

    public List<Entity[]> potentialPairs(List<Entity> ents){
        Map<CellKey, List<Entity>> grid = new HashMap<>();
        for (Entity e: ents){
            int cx = (int)Math.floor(e.getPosition().x / cellSize);
            int cy = (int)Math.floor(e.getPosition().y / cellSize);
            int cz = (int)Math.floor(e.getPosition().z / cellSize);
            CellKey key = new CellKey(cx,cy,cz);
            grid.computeIfAbsent(key,k->new ArrayList<>()).add(e);
        }
        List<Entity[]> pairs = new ArrayList<>();
        for (List<Entity> bucket: grid.values()){
            int n=bucket.size();
            for (int i=0;i<n;i++) for (int j=i+1;j<n;j++) pairs.add(new Entity[]{bucket.get(i), bucket.get(j)});
        }
        return pairs;
    }
}
