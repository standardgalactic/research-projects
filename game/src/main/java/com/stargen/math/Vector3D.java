package com.stargen.math;

public class Vector3D {
    public float x, y, z;

    public Vector3D(float x, float y, float z) { this.x = x; this.y = y; this.z = z; }

    public Vector3D add(Vector3D o){ return new Vector3D(x+o.x, y+o.y, z+o.z); }
    public Vector3D sub(Vector3D o){ return new Vector3D(x-o.x, y-o.y, z-o.z); }
    public Vector3D multiply(float s){ return new Vector3D(x*s, y*s, z*s); }

    public float length(){ return (float)Math.sqrt(x*x+y*y+z*z); }

    public Vector3D normalize(){
        float L = length();
        if (L <= 1e-6f) return new Vector3D(0,0,0);
        return new Vector3D(x/L, y/L, z/L);
    }

    @Override public String toString(){ return "Vector3D(" + x + "," + y + "," + z + ")"; }
}
