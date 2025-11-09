package com.stargen.world;

import java.util.*;

public class NavMesh {
    public static class Node {
        public final int x,y,z, id;
        public final List<Integer> edges = new ArrayList<>();
        Node(int id,int x,int y,int z){ this.id=id; this.x=x; this.y=y; this.z=z; }
    }
    public final List<Node> nodes = new ArrayList<>();

    public static NavMesh fromTunnel(TunnelLevel lvl){
        NavMesh g = new NavMesh();
        int W=lvl.W, H=lvl.H, D=lvl.D;
        int[][][] id = new int[W][H][D];
        for(int x=0;x<W;x++) for(int y=0;y<H;y++) for(int z=0;z<D;z++) id[x][y][z]=-1;
        // create nodes in empty voxels
        for(int x=0;x<W;x++) for(int y=0;y<H;y++) for(int z=0;z<D;z++){
            if (!lvl.solid[x][y][z]){
                int nid = g.nodes.size();
                id[x][y][z]=nid;
                g.nodes.add(new Node(nid,x,y,z));
            }
        }
        int[][] d = {{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
        for (Node n : g.nodes){
            for (int[] dv : d){
                int nx=n.x+dv[0], ny=n.y+dv[1], nz=n.z+dv[2];
                if (nx>=0 && ny>=0 && nz>=0 && nx<W && ny<H && nz<D && !lvl.solid[nx][ny][nz]){
                    int to = id[nx][ny][nz];
                    if (to>=0) n.edges.add(to);
                }
            }
        }
        return g;
    }

    public List<Integer> bfs(int startId, int goalId){
        int n = nodes.size();
        boolean[] vis = new boolean[n];
        int[] prev = new int[n];
        Arrays.fill(prev, -1);
        Deque<Integer> q = new ArrayDeque<>();
        q.add(startId); vis[startId]=true;
        while(!q.isEmpty()){
            int u = q.remove();
            if (u==goalId) break;
            for (int v : nodes.get(u).edges){
                if (!vis[v]){ vis[v]=true; prev[v]=u; q.add(v); }
            }
        }
        if (!vis[goalId]) return List.of();
        List<Integer> path = new ArrayList<>();
        for(int cur=goalId; cur!=-1; cur=prev[cur]) path.add(cur);
        Collections.reverse(path);
        return path;
    }
}
