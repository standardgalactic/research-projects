import bpy
import random

size=10

for x in range(size):
    for y in range(size):
        spin=random.choice([-1,1])

        color=(1,0,0,1) if spin==1 else (0,0,1,1)

        bpy.ops.mesh.primitive_cube_add(size=0.8, location=(x,y,0))

        obj=bpy.context.object

        mat=bpy.data.materials.new("spin")
        mat.diffuse_color=color

        obj.data.materials.append(mat)
