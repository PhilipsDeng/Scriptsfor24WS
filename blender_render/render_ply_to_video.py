import bpy
import os
import re
import math
# "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" --background --python "C:\Users\Philips Deng\Documents\GitHub\Scriptsfor24WS\render_ply_to_video.py"


bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


base_path = "C:/Users/Philips Deng/Desktop/dragonOLO_act17/"
# C:\Users\Philips Deng\Desktop\dragon\jeep car
all_files = os.listdir(base_path)

def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')
obj_files = sorted([f for f in all_files if f.endswith('.obj')], key=extract_number)
textures = sorted([f for f in all_files if f.endswith('.png')], key=extract_number)

# 动画设置
frame_start = 1
frame_end = 150
frame_step = 2  


bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'


bpy.context.scene.eevee.taa_render_samples = 16  # 设置采样数量
bpy.context.scene.eevee.use_gtao = True  # 启用屏幕空间环境光遮蔽


bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0, 0, 0, 1)  # 设置背景颜色为纯黑色

def create_area_light(name, location, rotation_euler, energy=15000, size=50):
    """
    创建一个AREA光源并将其添加到当前场景中。

    :param name: 光源名称
    :param location: 光源位置（元组）
    :param rotation_euler: 光源旋转（弧度）
    :param energy: 光源能量
    :param size: 光源大小
    :return: 创建的光源对象
    """
    light_data = bpy.data.lights.new(name=name, type='AREA')
    light_data.energy = energy
    light_data.size = size

    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = location
    light_object.rotation_euler = rotation_euler

    return light_object


# 前部光源
front_light = create_area_light(
    name="FrontAreaLight",
    location=(0, -20, 10),
    rotation_euler=(math.radians(90), 0, 0)
)

# 后部光源
back_light = create_area_light(
    name="BackAreaLight",
    location=(0, 20, 10),
    rotation_euler=(math.radians(-90), 0, 0)

)

# # 底部光源
# bottom_light = create_area_light(
#     name="BottomAreaLight",
#     location=(0, 0, -20),
#     rotation_euler=(math.radians(180), 0, 0)
# )



loaded_objects = []
for obj_file in obj_files:
    bpy.ops.wm.obj_import(filepath=base_path + obj_file)
    obj = bpy.context.selected_objects[0]

    for texture_file in textures:
        mat = bpy.data.materials.new(name=f"Material_{texture_file}")
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

        # 设置漫反射和镜面反射属性
        bsdf_node.inputs['Metallic'].default_value = 0.5
        bsdf_node.inputs['Roughness'].default_value = 0.7

        obj.data.materials.clear()
        obj.data.materials.append(mat)

        # 设置动画帧
        bpy.context.scene.frame_start = frame_start
        bpy.context.scene.frame_end = frame_end

        camera_data = bpy.data.cameras.new(name="Camera")
        camera_object = bpy.data.objects.new("Camera", camera_data)
        bpy.context.collection.objects.link(camera_object)
        bpy.context.scene.camera = camera_object
        camera_object.location = (0, -15, 9)
        # camera_object.location = (0, -1.5, 1)
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

        # 设置渲染输出路径和文件名
        bpy.context.scene.render.filepath = base_path + texture_file.replace('.png', '.mp4')
        bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
        bpy.context.scene.render.ffmpeg.format = 'MPEG4'
        bpy.context.scene.render.ffmpeg.codec = 'H264'
        bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'

        bpy.context.scene.render.resolution_x = 1920  
        bpy.context.scene.render.resolution_y = 1080  
        bpy.context.scene.render.fps = 30  

        # 渲染动画
        bpy.ops.render.render(animation=True)

    # 删除当前导入的对象
    bpy.data.objects.remove(obj, do_unlink=True)

# for i, (obj_file, texture_file) in enumerate(zip(reversed(obj_files), reversed(textures))):

#     bpy.ops.wm.obj_import(filepath=base_path + obj_file)
#     obj = bpy.context.selected_objects[0]
#     loaded_objects.append(obj)
    

#     mat = bpy.data.materials.new(name=f"Material_{i}")
#     mat.use_nodes = True
#     nodes = mat.node_tree.nodes
#     links = mat.node_tree.links


#     for node in nodes:
#         nodes.remove(node)


#     bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
#     output_node = nodes.new(type="ShaderNodeOutputMaterial")
#     links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])


#     tex_image_node = nodes.new(type="ShaderNodeTexImage")
#     tex_image_node.image = bpy.data.images.load(filepath=base_path + texture_file)
#     links.new(tex_image_node.outputs['Color'], bsdf_node.inputs['Base Color'])


#     bsdf_node.inputs['Metallic'].default_value = 0.5
#     bsdf_node.inputs['Roughness'].default_value = 0.7

#     obj.data.materials.append(mat)


# num_objects = len(loaded_objects)
# cycle_frames = num_objects * frame_step * 2 


# num_cycles = frame_end // cycle_frames + 1


# current_frame = frame_start
# for cycle in range(num_cycles):

#     for i, obj in enumerate(loaded_objects):

#         for other_obj in loaded_objects:
#             other_obj.hide_render = True
#             other_obj.hide_viewport = True
#             other_obj.keyframe_insert(data_path="hide_render", frame=current_frame)
#             other_obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        

#         obj.hide_render = False
#         obj.hide_viewport = False
#         obj.keyframe_insert(data_path="hide_render", frame=current_frame)
#         obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        

#         current_frame += frame_step
#         obj.keyframe_insert(data_path="hide_render", frame=current_frame)
#         obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
    

#     for i, obj in enumerate(reversed(loaded_objects)):

#         for other_obj in loaded_objects:
#             other_obj.hide_render = True
#             other_obj.hide_viewport = True
#             other_obj.keyframe_insert(data_path="hide_render", frame=current_frame)
#             other_obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        

#         obj.hide_render = False
#         obj.hide_viewport = False
#         obj.keyframe_insert(data_path="hide_render", frame=current_frame)
#         obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        

#         current_frame += frame_step
#         obj.keyframe_insert(data_path="hide_render", frame=current_frame)
#         obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)


#     if current_frame > frame_end:
#         break


# bpy.context.scene.frame_start = frame_start
# bpy.context.scene.frame_end = frame_end


# camera_data = bpy.data.cameras.new(name="Camera")
# camera_object = bpy.data.objects.new("Camera", camera_data)
# bpy.context.collection.objects.link(camera_object)
# bpy.context.scene.camera = camera_object
# camera_object.location = (0, -15, 8)
# camera_object.rotation_euler = (math.radians(63), 0, 0) 
# camera_data.lens = 20


# empty = bpy.data.objects.new("Empty", None)
# bpy.context.collection.objects.link(empty)
# camera_object.parent = empty

# for frame in range(frame_start, frame_end + 1):
#     bpy.context.scene.frame_set(frame)
#     angle = (frame - frame_start) * (2 * math.pi / frame_end)
#     empty.rotation_euler = (0, 0, angle)
#     empty.keyframe_insert(data_path="rotation_euler", index=-1)


# bpy.context.scene.render.filepath = base_path + "animation.mp4"
# bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
# bpy.context.scene.render.ffmpeg.format = 'MPEG4'
# bpy.context.scene.render.ffmpeg.codec = 'H264'
# bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'


# bpy.context.scene.render.resolution_x = 1920  
# bpy.context.scene.render.resolution_y = 1080  
# bpy.context.scene.render.fps = 15  


# bpy.ops.render.render(animation=True)