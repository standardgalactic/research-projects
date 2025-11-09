package com.stargen.io;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import com.stargen.world.TunnelLevel;

public class LevelLoader {
    public static class Result {
        public final TunnelLevel level;
        public final int sx, sy, sz;
        public final int gx, gy, gz;
        public Result(TunnelLevel level, int sx,int sy,int sz,int gx,int gy,int gz){
            this.level = level; this.sx=sx; this.sy=sy; this.sz=sz; this.gx=gx; this.gy=gy; this.gz=gz;
        }
    }

    // ASCII map format: lines are Z, rows are Y, columns are X; blocks for Z separated by blank line
    // Legend: '#' wall, '.' empty, 'S' start, 'G' goal
    public static Result load(String path) throws IOException {
        List<String> lines = Files.readAllLines(Paths.get(path));
        List<List<String>> slices = new ArrayList<>();
        List<String> current = new ArrayList<>();
        for (String ln: lines){
            if (ln.trim().isEmpty()){
                if (!current.isEmpty()){ slices.add(current); current = new ArrayList<>(); }
            } else {
                current.add(ln);
            }
        }
        if (!current.isEmpty()) slices.add(current);

        int D = slices.size();
        int H = slices.get(0).size();
        int W = slices.get(0).get(0).length();
        TunnelLevel lvl = new TunnelLevel(W,H,D);
        int sx=0,sy=0,sz=0,gx=W-1,gy=H-1,gz=D-1;

        for (int z=0; z<D; z++){
            List<String> slice = slices.get(z);
            for (int y=0; y<H; y++){
                String row = slice.get(y);
                for (int x=0; x<W; x++){
                    char c = row.charAt(x);
                    if (c == '#') lvl.solid[x][y][z] = true;
                    else lvl.solid[x][y][z] = false;
                    if (c == 'S'){ sx=x; sy=y; sz=z; }
                    if (c == 'G'){ gx=x; gy=y; gz=z; }
                }
            }
        }
        return new Result(lvl, sx,sy,sz, gx,gy,gz);
    }
}
