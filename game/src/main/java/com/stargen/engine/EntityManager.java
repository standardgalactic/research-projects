package com.stargen.engine;

import java.util.*;
import com.stargen.entities.Entity;

public class EntityManager {
    private final List<Entity> list = new ArrayList<>();
    public void add(Entity e){ list.add(e); }
    public void remove(Entity e){ list.remove(e); }
    public List<Entity> all(){ return list; }
}
