package com.stargen.world;

import java.lang.reflect.*;
import java.util.*;
import com.stargen.math.Vector3D;

public class NavHelper {

    public static int nearestIndex(NavMesh nav, float x, float y, float z){
        try {
            Field nodesField = nav.getClass().getField("nodes");
            Object nodesObj = nodesField.get(nav);
            if (nodesObj instanceof List){
                List<?> nodes = (List<?>) nodesObj;
                double best = Double.MAX_VALUE;
                int bestIdx = 0;
                for (int i=0;i<nodes.size();i++){
                    Object n = nodes.get(i);
                    double dx=0, dy=0, dz=0;
                    boolean ok=false;

                    // case A: node has public floats x,y,z
                    try{
                        Field fx = n.getClass().getField("x");
                        Field fy = n.getClass().getField("y");
                        Field fz = n.getClass().getField("z");
                        dx = ((Number)fx.get(n)).doubleValue() - x;
                        dy = ((Number)fy.get(n)).doubleValue() - y;
                        dz = ((Number)fz.get(n)).doubleValue() - z;
                        ok = true;
                    } catch(Exception ignore){}

                    // case B: node has Vector3D p
                    if (!ok){
                        try{
                            Field fp = n.getClass().getField("p");
                            Object pv = fp.get(n);
                            if (pv instanceof Vector3D){
                                Vector3D p = (Vector3D) pv;
                                dx = p.x - x;
                                dy = p.y - y;
                                dz = p.z - z;
                                ok = true;
                            }
                        } catch(Exception ignore){}
                    }

                    // case C: getters getX/getY/getZ
                    if (!ok){
                        try{
                            Method mx = n.getClass().getMethod("getX");
                            Method my = n.getClass().getMethod("getY");
                            Method mz = n.getClass().getMethod("getZ");
                            dx = ((Number)mx.invoke(n)).doubleValue() - x;
                            dy = ((Number)my.invoke(n)).doubleValue() - y;
                            dz = ((Number)mz.invoke(n)).doubleValue() - z;
                            ok = true;
                        } catch(Exception ignore){}
                    }

                    if (!ok) continue;
                    double d2 = dx*dx + dy*dy + dz*dz;
                    if (d2 < best){ best = d2; bestIdx = i; }
                }
                return bestIdx;
            }
        } catch (Exception e){
            // fallthrough
        }
        return 0; // fallback
    }
}
