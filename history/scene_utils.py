import bpy
import math
import random
from mathutils import Vector

def ensure_collection(name: str):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

def make_material(name: str, rgba=(1,1,1,1), emission=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Emission"].default_value = (rgba[0], rgba[1], rgba[2], 1.0)
    bsdf.inputs["Emission Strength"].default_value = emission

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

def add_sphere(location, radius=0.12, name="event", material=None, collection=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    if material:
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    if collection:
        collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)
    return obj

def add_cylinder_edge(p1, p2, radius=0.03, name="edge", material=None, collection=None):
    p1 = Vector(p1)
    p2 = Vector(p2)
    mid = (p1 + p2) / 2.0
    direction = p2 - p1
    length = direction.length
    if length < 1e-8:
        return None

    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=mid)
    obj = bpy.context.object
    obj.name = name

    z = Vector((0, 0, 1))
    direction_n = direction.normalized()
    axis = z.cross(direction_n)
    if axis.length > 1e-8:
        angle = z.angle(direction_n)
        obj.rotation_mode = "AXIS_ANGLE"
        obj.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)
    else:
        if z.dot(direction_n) < 0:
            obj.rotation_euler = (math.pi, 0, 0)

    if material:
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    if collection:
        collection.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)
    return obj

def add_camera_and_light(camera_loc=(8, -8, 6), look_at=(3, 0, 0), sun_loc=(6, -6, 10)):
    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = camera_loc
    cam.rotation_mode = "XYZ"
    cam.rotation_euler = look_at_rotation(cam.location, Vector(look_at))
    bpy.context.scene.camera = cam

    light_data = bpy.data.lights.new(name="Sun", type="SUN")
    light = bpy.data.objects.new(name="Sun", object_data=light_data)
    bpy.context.scene.collection.objects.link(light)
    light.location = sun_loc
    light_data.energy = 3.0

def look_at_rotation(camera_location, target):
    forward = (target - Vector(camera_location)).normalized()
    up = Vector((0, 0, 1))
    right = forward.cross(up).normalized()
    up2 = right.cross(forward).normalized()
    rot = (right, up2, -forward)
    return Matrix_from_basis(rot).to_euler()

def Matrix_from_basis(basis):
    import mathutils
    m = mathutils.Matrix((
        (basis[0].x, basis[1].x, basis[2].x),
        (basis[0].y, basis[1].y, basis[2].y),
        (basis[0].z, basis[1].z, basis[2].z),
    ))
    return m
