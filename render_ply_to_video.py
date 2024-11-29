import bpy
import os
import re
import math
# "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" --background --python "C:\Users\Philips Deng\Documents\GitHub\Scriptsfor24WS\render_ply_to_video.py"


bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


base_path = "C:/Users/Philips Deng/Desktop/dragon/video1/"

all_files = os.listdir(base_path)


obj_files = sorted([f for f in all_files if f.endswith('.obj')], key=lambda x: int(re.search(r'\d+', x).group()))
textures = sorted([f for f in all_files if f.endswith('.png')], key=lambda x: int(re.search(r'\d+', x).group()))

# 动画设置
frame_start = 1
frame_end = 300
frame_step = 3  


bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'


bpy.context.scene.eevee.taa_render_samples = 32  # 设置采样数量
bpy.context.scene.eevee.use_gtao = True  # 启用屏幕空间环境光遮蔽


bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0, 0, 0, 1)  # 设置背景颜色为纯黑色


top_light_data = bpy.data.lights.new(name="TopAreaLight", type='AREA')
top_light_data.size = 100
top_light_data.energy = 100000
top_light_object = bpy.data.objects.new(name="TopAreaLight", object_data=top_light_data)
bpy.context.collection.objects.link(top_light_object)
top_light_object.location = (0, 0, 10)


loaded_objects = []


for i, (obj_file, texture_file) in enumerate(zip(reversed(obj_files), reversed(textures))):

    bpy.ops.wm.obj_import(filepath=base_path + obj_file)
    obj = bpy.context.selected_objects[0]
    loaded_objects.append(obj)
    

    mat = bpy.data.materials.new(name=f"Material_{i}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links


    for node in nodes:
        nodes.remove(node)


    bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])


    tex_image_node = nodes.new(type="ShaderNodeTexImage")
    tex_image_node.image = bpy.data.images.load(filepath=base_path + texture_file)
    links.new(tex_image_node.outputs['Color'], bsdf_node.inputs['Base Color'])


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
camera_object.location = (0, -15, 11)
camera_object.rotation_euler = (math.radians(63), 0, 0) 
camera_data.lens = 20


empty = bpy.data.objects.new("Empty", None)
bpy.context.collection.objects.link(empty)
camera_object.parent = empty

for frame in range(frame_start, frame_end + 1):
    bpy.context.scene.frame_set(frame)
    angle = (frame - frame_start) * (2 * math.pi / frame_end)
    empty.rotation_euler = (0, 0, angle)
    empty.keyframe_insert(data_path="rotation_euler", index=-1)


bpy.context.scene.render.filepath = base_path + "animation.mp4"
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'


bpy.context.scene.render.resolution_x = 1920  
bpy.context.scene.render.resolution_y = 1080  
bpy.context.scene.render.fps = 60  


bpy.ops.render.render(animation=True)