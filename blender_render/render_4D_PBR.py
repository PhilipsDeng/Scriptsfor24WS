import bpy
import os
import re
import math
'''
blender --background --python /root/Scriptsfor24WS/blender_render/render_4D_PBR.py
'''

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

base_path = "/home/philipsdeng/文档/GitHub/Scriptsfor24WS"
obj_path = os.path.join(base_path, "data/dragonOLO_act17/")
all_files = os.listdir(obj_path)
obj_files = sorted([f for f in all_files if f.endswith('.obj')], key=lambda x: int(re.search(r'\d+', x).group()))

frame_start = 1
frame_end = 300
frame_step = 2

bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
bpy.context.scene.eevee.taa_render_samples = 16
bpy.context.scene.eevee.use_gtao = False

bpy.context.scene.world.use_nodes = True
world = bpy.context.scene.world
node_tree = world.node_tree
nodes = node_tree.nodes
links = node_tree.links
for node in nodes:
    nodes.remove(node)
env_texture_node = nodes.new(type="ShaderNodeTexEnvironment")
env_texture_node.location = (-300, 0)
hdr_path = os.path.join(obj_path, "probe.hdr")
if os.path.exists(hdr_path):
    env_texture_node.image = bpy.data.images.load(filepath=hdr_path)
bg_node = nodes.new(type="ShaderNodeBackground")
bg_node.location = (0, 0)
bg_node.inputs['Strength'].default_value = 0.8
output_node = nodes.new(type="ShaderNodeOutputWorld")
output_node.location = (200, 0)
links.new(env_texture_node.outputs['Color'], bg_node.inputs['Color'])
links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

loaded_objects = []
for i, obj_file in enumerate(obj_files):
    bpy.ops.wm.obj_import(filepath=os.path.join(obj_path, obj_file))
    obj = bpy.context.selected_objects[0]
    loaded_objects.append(obj)
    mat = bpy.data.materials.new(name=f"Material_{i}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for node in nodes:
        nodes.remove(node)
    bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf_node.location = (0, 0)
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    output_node.location = (200, 0)
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])
    base_color_node = nodes.new(type="ShaderNodeTexImage")
    base_color_node.location = (-400, 200)
    albedo_path = os.path.join(obj_path, "texture_kd.png")
    if os.path.exists(albedo_path):
        base_color_path = albedo_path
    else:
        break
    base_color_node.image = bpy.data.images.load(filepath=base_color_path)
    links.new(base_color_node.outputs['Color'], bsdf_node.inputs['Base Color'])
    metallic_node = nodes.new(type="ShaderNodeTexImage")
    metallic_node.location = (-400, 0)
    metallic_path = os.path.join(obj_path, "texture_metallic.png")
    if os.path.exists(metallic_path):
        metallic_node.image = bpy.data.images.load(filepath=metallic_path)
        metallic_node.image.colorspace_settings.name = 'Non-Color'
        links.new(metallic_node.outputs['Color'], bsdf_node.inputs['Metallic'])
    else:
        bsdf_node.inputs['Metallic'].default_value = 0.0
    roughness_node = nodes.new(type="ShaderNodeTexImage")
    roughness_node.location = (-400, -200)
    roughness_path = os.path.join(obj_path, "texture_roughness.png")
    if os.path.exists(roughness_path):
        roughness_node.image = bpy.data.images.load(filepath=roughness_path)
        roughness_node.image.colorspace_settings.name = 'Non-Color'
        links.new(roughness_node.outputs['Color'], bsdf_node.inputs['Roughness'])
    else:
        bsdf_node.inputs['Roughness'].default_value = 0.8
    normal_tex_node = nodes.new(type="ShaderNodeTexImage")
    normal_tex_node.location = (-400, -400)
    normal_path = os.path.join(obj_path, "texture_n.png")
    if os.path.exists(normal_path):
        normal_tex_node.image = bpy.data.images.load(filepath=normal_path)
        normal_tex_node.image.colorspace_settings.name = 'Non-Color'
        normal_map_node = nodes.new(type="ShaderNodeNormalMap")
        normal_map_node.location = (-200, -400)
        links.new(normal_tex_node.outputs['Color'], normal_map_node.inputs['Color'])
        links.new(normal_map_node.outputs['Normal'], bsdf_node.inputs['Normal'])
    obj.data.materials.append(mat)

num_objects = len(loaded_objects)
cycle_frames = num_objects * frame_step * 2
num_cycles = frame_end // cycle_frames + 1
current_frame = frame_start
for cycle in range(num_cycles):
    for i, obj in enumerate(loaded_objects):
        for other_obj in loaded_objects:
            other_obj.hide_render = True
            other_obj.hide_viewport = True
            other_obj.keyframe_insert(data_path="hide_render", frame=current_frame)
            other_obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        obj.hide_render = False
        obj.hide_viewport = False
        obj.keyframe_insert(data_path="hide_render", frame=current_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        current_frame += frame_step
        obj.keyframe_insert(data_path="hide_render", frame=current_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
    for i, obj in enumerate(reversed(loaded_objects)):
        for other_obj in loaded_objects:
            other_obj.hide_render = True
            other_obj.hide_viewport = True
            other_obj.keyframe_insert(data_path="hide_render", frame=current_frame)
            other_obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        obj.hide_render = False
        obj.hide_viewport = False
        obj.keyframe_insert(data_path="hide_render", frame=current_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        current_frame += frame_step
        obj.keyframe_insert(data_path="hide_render", frame=current_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
    if current_frame > frame_end:
        break

bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = frame_end

camera_data = bpy.data.cameras.new(name="Camera")
camera_object = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
bpy.context.scene.camera = camera_object

#-------------------------------------------CAM-DIST--------------------------------------------------------#

# camera_object.location = (0, -5, 3)
# camera_object.location = (0, -15, 9)
camera_object.location = (0, -3, 2)


#-----------------------------------------------------------------------------------------------------------#

camera_object.rotation_euler = (math.radians(62), 0, 0)
camera_data.lens = 30

empty = bpy.data.objects.new("Empty", None)
bpy.context.collection.objects.link(empty)
camera_object.parent = empty

for frame in range(frame_start, frame_end + 1):
    bpy.context.scene.frame_set(frame)
    angle = -(frame - frame_start) * (2 * math.pi / (frame_end * 5))
    empty.rotation_euler = (0, 0, angle)
    empty.keyframe_insert(data_path="rotation_euler", index=-1)

bpy.context.scene.render.filepath = os.path.join(base_path, "data/outputs/animation.mp4")
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.fps = 30

bpy.ops.render.render(animation=True)

if __name__ == '__main__':
    pass
