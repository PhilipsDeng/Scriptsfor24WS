import bpy
import os
import re
import math
import mathutils
# "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" --background --python "C:\Users\Philips Deng\Documents\GitHub\Scriptsfor24WS\blender_render\render_4D_PBR_img.py"


def get_max_distance_from_origin(obj):
    max_dist = 0.0
    for vertex in obj.data.vertices:
        global_co = obj.matrix_world @ vertex.co  
        dist = global_co.length  
        if dist > max_dist:
            max_dist = dist
    return max_dist


bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
bpy.context.scene.eevee.taa_render_samples = 128
bpy.context.scene.eevee.use_gtao = True


# ------------------------ 1. 清空场景 ------------------------
# 删除场景中所有对象，确保干净的工作环境
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ------------------------ 2. 加载单一 OBJ 模型 ------------------------
# 设置基础路径和 OBJ 文件的路径（请根据实际情况修改文件名）
base_path = r"C:\Users\Philips Deng\Documents\GitHub\Scriptsfor24WS\data\dreammat\deer\it4000-export"
obj_filepath = os.path.join(base_path, r"model.obj")
if os.path.exists(obj_filepath):
    bpy.ops.wm.obj_import(filepath=obj_filepath)
    obj = bpy.context.selected_objects[0]
    obj.rotation_euler = (math.radians(0), math.radians(0), math.radians(-90))
    image_path = "deer_r20"
else:
    raise Exception("找不到指定的 OBJ 文件: " + obj_filepath)

# ------------------------ 3. 设置 HDR 环境光 ------------------------
# 为了更真实的光照效果，我们使用 HDR 环境贴图
scene = bpy.context.scene
scene.world.use_nodes = True
world = scene.world
node_tree = world.node_tree
nodes = node_tree.nodes
links = node_tree.links

# 删除所有默认节点
for node in nodes:
    nodes.remove(node)

# 创建 HDR 环境纹理节点，并加载 HDR 图片
env_texture_node = nodes.new(type="ShaderNodeTexEnvironment")
env_texture_node.location = (-300, 0)
hdr_filepath = r"C:\Users\Philips Deng\Documents\GitHub\Scriptsfor24WS\data\dragonOLO_act17\probe.hdr"
if os.path.exists(hdr_filepath):
    env_texture_node.image = bpy.data.images.load(filepath=hdr_filepath)
else:
    raise Exception("找不到 HDR 文件: " + hdr_filepath)

# 创建背景节点并设置亮度（Strength 可根据需求调整）
bg_node = nodes.new(type="ShaderNodeBackground")
bg_node.location = (0, 0)
bg_node.inputs['Strength'].default_value = 1.5

# 创建输出节点，用于将背景效果输出到世界上
output_node = nodes.new(type="ShaderNodeOutputWorld")
output_node.location = (200, 0)

# 将节点连接起来：HDR纹理 → 背景 → 输出
links.new(env_texture_node.outputs['Color'], bg_node.inputs['Color'])
links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

# ------------------------ 4. 创建完整的 PBR 材质 ------------------------
# 为加载的模型创建一个新的材质，并启用节点系统
mat = bpy.data.materials.new(name="PBR_Material")
mat.use_nodes = True
mat_nodes = mat.node_tree.nodes
mat_links = mat.node_tree.links

# 清除默认节点（比如默认的“Principled BSDF”和“Material Output”）
for node in mat_nodes:
    mat_nodes.remove(node)

# 创建 Principled BSDF 节点（核心 PBR 着色器）
bsdf_node = mat_nodes.new(type="ShaderNodeBsdfPrincipled")
bsdf_node.location = (0, 0)

# 创建材质输出节点
mat_output_node = mat_nodes.new(type="ShaderNodeOutputMaterial")
mat_output_node.location = (300, 0)
mat_links.new(bsdf_node.outputs['BSDF'], mat_output_node.inputs['Surface'])

# -------------------- 加载并连接各个纹理 --------------------

# 4.1 Base Color (Albedo)
base_color_node = mat_nodes.new(type="ShaderNodeTexImage")
base_color_node.location = (-400, 200)
albedo_path = os.path.join(base_path, "texture_kd.jpg")
if os.path.exists(albedo_path):
    base_color_node.image = bpy.data.images.load(filepath=albedo_path)
    mat_links.new(base_color_node.outputs['Color'], bsdf_node.inputs['Base Color'])
else:
    print("未找到 Base Color 纹理，使用默认颜色")

# 4.2 Metallic
metallic_node = mat_nodes.new(type="ShaderNodeTexImage")
metallic_node.location = (-400, 0)
metallic_path = os.path.join(base_path, "texture_metallic.png")
if os.path.exists(metallic_path):
    metallic_node.image = bpy.data.images.load(filepath=metallic_path)
    # Metallic 通道通常不需要颜色管理，设置为 Non-Color
    metallic_node.image.colorspace_settings.name = 'Non-Color'
    mat_links.new(metallic_node.outputs['Color'], bsdf_node.inputs['Metallic'])
else:
    bsdf_node.inputs['Metallic'].default_value = 0.0

# 4.3 Roughness
roughness_node = mat_nodes.new(type="ShaderNodeTexImage")
roughness_node.location = (-400, -200)
roughness_path = os.path.join(base_path, "texture_roughness.png")
if os.path.exists(roughness_path):
    roughness_node.image = bpy.data.images.load(filepath=roughness_path)
    roughness_node.image.colorspace_settings.name = 'Non-Color'
    mat_links.new(roughness_node.outputs['Color'], bsdf_node.inputs['Roughness'])
else:
    bsdf_node.inputs['Roughness'].default_value = 0.8

# 4.4 Normal Map
normal_tex_node = mat_nodes.new(type="ShaderNodeTexImage")
normal_tex_node.location = (-400, -400)
normal_path = os.path.join(base_path, "texture_n.png")
if os.path.exists(normal_path):
    normal_tex_node.image = bpy.data.images.load(filepath=normal_path)
    normal_tex_node.image.colorspace_settings.name = 'Non-Color'
    # 创建 Normal Map 节点来处理法线贴图
    normal_map_node = mat_nodes.new(type="ShaderNodeNormalMap")
    normal_map_node.location = (-200, -400)
    mat_links.new(normal_tex_node.outputs['Color'], normal_map_node.inputs['Color'])
    mat_links.new(normal_map_node.outputs['Normal'], bsdf_node.inputs['Normal'])
else:
    print("未找到 Normal Map 纹理，跳过法线贴图设置")

# 将创建的材质赋给加载的对象
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# ------------------------ 5. 设置相机 ------------------------
# 创建一个新的相机对象，并添加到场景中
camera_data = bpy.data.cameras.new(name="Camera")
camera_object = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
bpy.context.scene.camera = camera_object

# 设置相机位置和角度（可根据需要调整以获得合适的视角）
max_distance = get_max_distance_from_origin(obj)
dist = max_distance * 2.5

elev = math.radians(25)
azim = math.radians(-59)

x = dist * math.cos(elev) * math.sin(azim)
y = -dist * math.cos(elev) * math.cos(azim)
z = dist * math.sin(elev)
camera_object.location = (x, y, z)
print("摄像机位置:", camera_object.location)

direction = -camera_object.location

rot_quat = direction.to_track_quat('-Z', 'Y')
camera_object.rotation_euler = rot_quat.to_euler()
print("摄像机旋转（欧拉角）:", camera_object.rotation_euler)

camera_data.lens = 50

# ------------------------ 6. 渲染设置 ------------------------
# 设置分辨率和其他渲染参数
scene.render.resolution_x = 3840
scene.render.resolution_y = 3840
scene.render.fps = 24  # 对静态图像无实际影响

# 设置输出文件路径和图片格式（PNG）
output_filepath = os.path.join(base_path, image_path + ".png")
scene.render.filepath = output_filepath
scene.render.image_settings.file_format = 'PNG'

# ------------------------ 7. 执行渲染 ------------------------
# 渲染当前帧，并将结果保存到指定路径
bpy.ops.render.render(write_still=True)