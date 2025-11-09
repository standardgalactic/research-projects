package com.stargen.entities.ai;

import java.util.*;
import com.stargen.world.NavMesh;
import com.stargen.world.NavMesh.Node;
import com.stargen.entities.Entity;
import com.stargen.math.Vector3D;

public class AIPathFollower extends Entity {
    private final NavMesh nav;
    private List<Integer> path = List.of();
    private int idx = 0;
    private float speed = 12f;

    public AIPathFollower(Vector3D pos, NavMesh nav){
        super(pos);
        this.nav = nav;
        this.radius = 1.5f;
        this.health = 50f;
    }

    public void follow(int startNode, int goalNode){
        this.path = nav.bfs(startNode, goalNode);
        this.idx = 0;
        if (path.isEmpty()) System.out.println("[AIPathFollower] No path found.");
    }

    @Override public void update(float dt){
        if (!active) return;
        if (path.isEmpty() || idx >= path.size()){ super.update(dt); return; }
        Node target = nav.nodes.get(path.get(idx));
        Vector3D tgt = new Vector3D(target.x, target.y, target.z);
        Vector3D dir = new Vector3D(tgt.x - position.x, tgt.y - position.y, tgt.z - position.z);
        float len = (float)Math.sqrt(dir.x*dir.x + dir.y*dir.y + dir.z*dir.z);
        if (len < 0.5f){ idx++; }
        else {
            dir.x /= len; dir.y /= len; dir.z /= len;
            velocity.x += dir.x * speed * dt;
            velocity.y += dir.y * speed * dt;
            velocity.z += dir.z * speed * dt;
        }
        super.update(dt);
    }
}
