import bpy
import os
import re
import math
'''
blender --background --python /root/Scriptsfor24WS/blender_render/render_4D_PBR_Cycles.py
blender --background --python /home/philipsdeng/文档/GitHub/Scriptsfor24WS/blender_render/render_4D_PBR_Cycles.py
'''

# 清空场景中的所有物体
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

base_path = "/home/philipsdeng/文档/GitHub/Scriptsfor24WS"
obj_path = os.path.join(base_path, "data/dear/")
all_files = os.listdir(obj_path)
obj_files = sorted([f for f in all_files if f.endswith('.obj')], key=lambda x: int(re.search(r'\d+', x).group()))

frame_start = 1
frame_end = 300
frame_step = 2

# 将渲染引擎设置为 Cycles，并设置相关参数
bpy.context.scene.render.engine = 'CYCLES'
# 如果你的电脑有支持 GPU 的显卡，可以启用 GPU 渲染，效果更快更好
# 注意：这里需要提前在 Blender 的用户偏好设置中启用 GPU 支持
# bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'  # 或 'OPTIX', 'HIP', 'METAL'
# bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 128  # 可根据需要调整采样数

# 设置世界环境（背景）节点
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
bg_node.inputs['Strength'].default_value = 1
output_node = nodes.new(type="ShaderNodeOutputWorld")
output_node.location = (200, 0)
links.new(env_texture_node.outputs['Color'], bg_node.inputs['Color'])
links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

# 导入 .obj 模型并为其创建材质
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
    
    # 加载 Base Color 纹理
    base_color_node = nodes.new(type="ShaderNodeTexImage")
    base_color_node.location = (-400, 200)
    albedo_path = os.path.join(obj_path, "texture_kd.png")
    if os.path.exists(albedo_path):
        base_color_node.image = bpy.data.images.load(filepath=albedo_path)
    else:
        break
    links.new(base_color_node.outputs['Color'], bsdf_node.inputs['Base Color'])
    
    # 加载 Metallic 纹理
    metallic_node = nodes.new(type="ShaderNodeTexImage")
    metallic_node.location = (-400, 0)
    metallic_path = os.path.join(obj_path, "texture_metallic.png")
    if os.path.exists(metallic_path):
        metallic_node.image = bpy.data.images.load(filepath=metallic_path)
        metallic_node.image.colorspace_settings.name = 'Non-Color'
        links.new(metallic_node.outputs['Color'], bsdf_node.inputs['Metallic'])
    else:
        bsdf_node.inputs['Metallic'].default_value = 0.0
        
    # 加载 Roughness 纹理
    roughness_node = nodes.new(type="ShaderNodeTexImage")
    roughness_node.location = (-400, -200)
    roughness_path = os.path.join(obj_path, "texture_roughness.png")
    if os.path.exists(roughness_path):
        roughness_node.image = bpy.data.images.load(filepath=roughness_path)
        roughness_node.image.colorspace_settings.name = 'Non-Color'
        links.new(roughness_node.outputs['Color'], bsdf_node.inputs['Roughness'])
    else:
        bsdf_node.inputs['Roughness'].default_value = 0.8
        
    # 加载 Normal 纹理并生成法线贴图
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

# 根据模型数量设置关键帧，实现前后切换显示效果
num_objects = len(loaded_objects)
cycle_frames = num_objects * frame_step * 2
num_cycles = frame_end // cycle_frames + 1
current_frame = frame_start
for cycle in range(num_cycles):
    for i, obj in enumerate(loaded_objects):
        # 隐藏所有物体
        for other_obj in loaded_objects:
            other_obj.hide_render = True
            other_obj.hide_viewport = True
            other_obj.keyframe_insert(data_path="hide_render", frame=current_frame)
            other_obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        # 显示当前物体
        obj.hide_render = False
        obj.hide_viewport = False
        obj.keyframe_insert(data_path="hide_render", frame=current_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        current_frame += frame_step
        obj.keyframe_insert(data_path="hide_render", frame=current_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
    # 反向显示物体
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

# 创建并设置摄像机
camera_data = bpy.data.cameras.new(name="Camera")
camera_object = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
bpy.context.scene.camera = camera_object
camera_object.location = (0, -5, 3)
# camera_object.location = (0, -15, 9)
camera_object.rotation_euler = (math.radians(62), 0, 0)
camera_data.lens = 20

# 创建空物体作为摄像机的父物体，实现围绕旋转的动画效果
empty = bpy.data.objects.new("Empty", None)
bpy.context.collection.objects.link(empty)
camera_object.parent = empty

# 为空物体设置旋转关键帧，使摄像机围绕场景旋转，就像在一个转盘上拍摄不同角度的照片
for frame in range(frame_start, frame_end + 1):
    bpy.context.scene.frame_set(frame)
    angle = -(frame - frame_start) * (2 * math.pi / (frame_end * 2))
    empty.rotation_euler = (0, 0, angle)
    empty.keyframe_insert(data_path="rotation_euler", index=-1)

# 设置输出路径及视频格式
bpy.context.scene.render.filepath = os.path.join(base_path, "data/outputs/animation_cycles.mp4")
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
