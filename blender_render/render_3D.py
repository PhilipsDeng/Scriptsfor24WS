import bpy
import os
import re
import math
import time
import mathutils


# "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" --background --python "C:\Users\Philips Deng\Documents\GitHub\Scriptsfor24WS\blender_render\render_3D.py"
# blender --background --python /root/autodl-tmp/Github/Scriptsfor24WS/blender_render/render_3D.py


crt_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


# blender --background --python render_4D.py

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)


# base_path = "C:/Users/Philips Deng/Desktop/dragonOLO_act17/"
base_path = r"C:\Users\Philips Deng\Documents\GitHub\Scriptsfor24WS\data\deer_ablation"

all_files = os.listdir(base_path)

obj_files = sorted([f for f in all_files if f.endswith('.obj')], key=lambda x: int(re.search(r'\d+', x).group()))
textures = ["texture.png"]

frame_start = 1
frame_end = 1
frame_step = 5  

bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'

bpy.context.scene.eevee.taa_render_samples = 128  # 设置采样数量
bpy.context.scene.eevee.use_gtao = False  # 启用屏幕空间环境光遮蔽

bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0, 0, 0, 1) 

bpy.context.scene.view_settings.view_transform = 'Standard'


def get_max_distance_from_origin(obj):
    max_dist = 0.0
    for vertex in obj.data.vertices:
        global_co = obj.matrix_world @ vertex.co  
        dist = global_co.length  
        if dist > max_dist:
            max_dist = dist
    return max_dist


def create_area_light(name, location, rotation_euler, energy=10000, size=20):
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


texture_path = os.path.join(base_path, textures[0])
if not bpy.data.images.get(textures[0]):
    tex_image = bpy.data.images.load(filepath=texture_path)
else:
    tex_image = bpy.data.images[textures[0]]

loaded_objects = []


target_obj_index = 0  
if target_obj_index < len(obj_files):
    obj_file = obj_files[target_obj_index]
    obj_path = os.path.join(base_path, obj_file)
    bpy.ops.wm.obj_import(filepath=obj_path)
    obj = bpy.context.selected_objects[0]
    loaded_objects.append(obj)

    # 创建新的材质
    mat = bpy.data.materials.new(name=f"Material_{target_obj_index}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for node in nodes:
        nodes.remove(node)

    bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

    tex_image_node = nodes.new(type="ShaderNodeTexImage")
    tex_image_node.image = bpy.data.images.load(filepath=os.path.join(base_path, textures[0]))
    links.new(tex_image_node.outputs['Color'], bsdf_node.inputs['Base Color'])

    bsdf_node.inputs['Metallic'].default_value = 0.1
    bsdf_node.inputs['Roughness'].default_value = 0.9

    obj.data.materials.append(mat)


bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = frame_end

camera_data = bpy.data.cameras.new(name="Camera")
camera_object = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
bpy.context.scene.camera = camera_object


mesh_obj = loaded_objects[0]  # 如果你有多个对象，选择需要的那个
max_distance = get_max_distance_from_origin(mesh_obj)
dist = max_distance * 2.5

elev = math.radians(30)
azim = math.radians(-50)

x = dist * math.cos(elev) * math.sin(azim)
y = -dist * math.cos(elev) * math.cos(azim)
z = dist * math.sin(elev)
camera_object.location = (x, y, z)
print("摄像机位置:", camera_object.location)

direction = -camera_object.location

rot_quat = direction.to_track_quat('-Z', 'Y')
camera_object.rotation_euler = rot_quat.to_euler()
print("摄像机旋转（欧拉角）:", camera_object.rotation_euler)

camera_object.location = camera_object.location + mathutils.Vector((0, 0, 0.5))
camera_data.lens = 50


empty = bpy.data.objects.new("Empty", None)
bpy.context.collection.objects.link(empty)
camera_object.parent = empty


# 固定设置一个角度，例如不旋转，保持初始角度
empty.rotation_euler = (0, 0, 0)
empty.keyframe_insert(data_path="rotation_euler", frame=frame_start)

bpy.context.scene.render.filepath = os.path.join(base_path, "render_still.png")
bpy.context.scene.render.image_settings.file_format = 'PNG'

bpy.context.scene.render.resolution_x = 3840  
bpy.context.scene.render.resolution_y = 3840  
bpy.context.scene.render.fps = 60  

# 渲染单帧
bpy.ops.render.render(write_still=True)

if __name__ == '__main__':
    pass
