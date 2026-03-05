import bpy
from mathutils import Vector

def sphere(p):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=p)

def edge(p1,p2):
    mid=(p1+p2)/2
    d=(p2-p1).length

    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=d, location=mid)

root=Vector((0,0,0))
a=Vector((2,1,0))
b=Vector((2,-1,0))
merge=Vector((4,0,0))

sphere(root)
sphere(a)
sphere(b)
sphere(merge)

edge(root,a)
edge(root,b)
edge(a,merge)
edge(b,merge)
