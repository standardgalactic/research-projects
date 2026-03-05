import bpy
import random
import math

def create_event(x,y,z):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(x,y,z))

def connect(p1,p2):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05,
        depth=((p1-p2).length),
        location=(p1+p2)/2
    )

events = []

for i in range(20):
    x=i*0.6
    y=random.uniform(-1,1)
    z=random.uniform(-1,1)

    create_event(x,y,z)
    events.append((x,y,z))
