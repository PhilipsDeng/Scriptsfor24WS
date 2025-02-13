import bpy
import os
import re
import math
'''
blender --background --python /root/Scriptsfor24WS/blender_render/render_4D_PBR.py
'''
# -------------------------------
# 清空场景中的所有物体
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# -------------------------------
# 设置文件路径与参数
# base_path = "/home/philipsdeng/文档/GitHub/2OTex/outputs/2025-01-06_18-45-30_vsd_a_fire_dragon,_photo_realistic,_8k,_hd,_3D_seed_1949_n_frames_20_n_particles_1/"
base_path = "/root/Scriptsfor24WS"

obj_path = os.path.join(base_path, "data/dragon_obj/")
texture_path =os.path.join(base_path, "data/texture/dragonOF2_act20/")

all_files = os.listdir(obj_path)
obj_files = sorted([f for f in all_files if f.endswith('.obj')], key=lambda x: int(re.search(r'\d+', x).group()))


# 动画参数
frame_start = 1
frame_end = 300
frame_step = 6  

# -------------------------------
# 渲染引擎与世界设置
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
bpy.context.scene.eevee.taa_render_samples = 16  # 采样数量
bpy.context.scene.eevee.use_gtao = False  # 禁用环境光遮蔽

bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0, 0, 0, 1)  # 背景颜色设为纯黑

# -------------------------------
# 定义创建区域光源的函数
def create_area_light(name, location, rotation_euler, energy=60000, size=100):
    """
    创建一个区域光源
    """
    light_data = bpy.data.lights.new(name=name, type='AREA')
    light_data.energy = energy
    light_data.size = size

    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = location
    light_object.rotation_euler = rotation_euler

    return light_object

# 创建前部和后部光源
front_light = create_area_light(
    name="FrontAreaLight",
    location=(0, -20, 10),
    rotation_euler=(math.radians(90), 0, 0)
)

back_light = create_area_light(
    name="BackAreaLight",
    location=(0, 20, 10),
    rotation_euler=(math.radians(-90), 0, 0)
)

# -------------------------------
# # 预加载基础贴图（Base Color），如果需要
# texture_path = os.path.join(texture_path, textures[0])
# if not bpy.data.images.get(textures[0]):
#     tex_image = bpy.data.images.load(filepath=texture_path)
# else:
#     tex_image = bpy.data.images[textures[0]]

loaded_objects = []

# -------------------------------
# 导入 OBJ 文件并为每个物体创建 PBR 材质（基于BRDF）
for i, obj_file in enumerate(obj_files):
    # 导入 OBJ 文件
    bpy.ops.wm.obj_import(filepath=os.path.join(obj_path, obj_file))
    obj = bpy.context.selected_objects[0]
    loaded_objects.append(obj)

    # 创建新的材质并启用节点
    mat = bpy.data.materials.new(name=f"Material_{i}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # 清空默认节点
    for node in nodes:
        nodes.remove(node)

    # 创建 Principled BSDF 节点（PBR 核心节点）
    bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf_node.location = (0, 0)

    # 创建材质输出节点
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    output_node.location = (200, 0)
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])



    base_color_node = nodes.new(type="ShaderNodeTexImage")
    base_color_node.location = (-400, 200)
    albedo_path = os.path.join(texture_path, "texture_kd.png")
     
    if os.path.exists(albedo_path):
        base_color_path = albedo_path
    else:
        break
    base_color_node.image = bpy.data.images.load(filepath=base_color_path)
    links.new(base_color_node.outputs['Color'], bsdf_node.inputs['Base Color'])


    metallic_node = nodes.new(type="ShaderNodeTexImage")
    metallic_node.location = (-400, 0)
    metallic_path = os.path.join(texture_path, "texture_metallic.png")
    if os.path.exists(metallic_path):
        metallic_node.image = bpy.data.images.load(filepath=metallic_path)
        metallic_node.image.colorspace_settings.name = 'Non-Color'
        links.new(metallic_node.outputs['Color'], bsdf_node.inputs['Metallic'])
    else:
        bsdf_node.inputs['Metallic'].default_value = 0.0


    roughness_node = nodes.new(type="ShaderNodeTexImage")
    roughness_node.location = (-400, -200)
    roughness_path = os.path.join(texture_path, "texture_roughness.png")
    if os.path.exists(roughness_path):
        roughness_node.image = bpy.data.images.load(filepath=roughness_path)
        roughness_node.image.colorspace_settings.name = 'Non-Color'
        links.new(roughness_node.outputs['Color'], bsdf_node.inputs['Roughness'])
    else:
        bsdf_node.inputs['Roughness'].default_value = 0.8


    normal_tex_node = nodes.new(type="ShaderNodeTexImage")
    normal_tex_node.location = (-400, -400)
    normal_path = os.path.join(texture_path, "texture_n.png")
    if os.path.exists(normal_path):
        normal_tex_node.image = bpy.data.images.load(filepath=normal_path)
        normal_tex_node.image.colorspace_settings.name = 'Non-Color'
        normal_map_node = nodes.new(type="ShaderNodeNormalMap")
        normal_map_node.location = (-200, -400)
        links.new(normal_tex_node.outputs['Color'], normal_map_node.inputs['Color'])
        links.new(normal_map_node.outputs['Normal'], bsdf_node.inputs['Normal'])

    # 将材质赋给当前物体
    obj.data.materials.append(mat)

# -------------------------------
# 以下部分保持动画设置与关键帧逻辑不变

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

# -------------------------------
# 设置摄像机和动画
camera_data = bpy.data.cameras.new(name="Camera")
camera_object = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
bpy.context.scene.camera = camera_object
camera_object.location = (0, -15, 9)
camera_object.rotation_euler = (math.radians(62), 0, 0) 
camera_data.lens = 20

empty = bpy.data.objects.new("Empty", None)
bpy.context.collection.objects.link(empty)
camera_object.parent = empty

for frame in range(frame_start, frame_end + 1):
    bpy.context.scene.frame_set(frame)
    angle = -(frame - frame_start) * (2 * math.pi / (frame_end * 2))
    empty.rotation_euler = (0, 0, angle)
    empty.keyframe_insert(data_path="rotation_euler", index=-1)

# -------------------------------
# 渲染设置
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
