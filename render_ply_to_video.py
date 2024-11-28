import bpy
import time
import math
# "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" --background --python "C:\Users\Philips Deng\Documents\GitHub\Scriptsfor24WS\render_ply_to_video.py"

# 删除默认场景中的所有对象
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 文件路径设置（更新为你的文件路径）
base_path = "C:/Users/Philips Deng/Desktop/dragon/video1/"  # 替换为你的文件路径
obj_files = ["mesh_24.obj", "mesh_25.obj", "mesh_26.obj"]
textures = ["frame24_texture.png", "frame25_texture.png", "frame26_texture.png"]

# 动画设置
frame_start = 1
frame_end = 150
frame_step = 5  # 每个对象显示的帧数

# 使用 Eevee 渲染引擎
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'

# 设置 Eevee 渲染参数
bpy.context.scene.eevee.taa_render_samples = 32  # 设置采样数量
bpy.context.scene.eevee.use_gtao = True  # 启用屏幕空间环境光遮蔽

# 设置纯黑色背景
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0, 0, 0, 1)  # 设置背景颜色为纯黑色

# 创建光源
top_light_data = bpy.data.lights.new(name="TopAreaLight", type='AREA')
top_light_data.size = 100
top_light_data.energy = 100000
top_light_object = bpy.data.objects.new(name="TopAreaLight", object_data=top_light_data)
bpy.context.collection.objects.link(top_light_object)
top_light_object.location = (0, 0, 10)

# 预加载对象和纹理
loaded_objects = []

# 倒序导入对象和纹理
for i, (obj_file, texture_file) in enumerate(zip(reversed(obj_files), reversed(textures))):
    # 导入 OBJ 文件
    bpy.ops.wm.obj_import(filepath=base_path + obj_file)
    obj = bpy.context.selected_objects[0]
    loaded_objects.append(obj)
    
    # 创建材质并绑定对应的纹理
    mat = bpy.data.materials.new(name=f"Material_{i}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # 清除默认节点
    for node in nodes:
        nodes.remove(node)

    # 添加 Principled BSDF 节点和材质输出节点
    bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

    # 添加纹理节点
    tex_image_node = nodes.new(type="ShaderNodeTexImage")
    tex_image_node.image = bpy.data.images.load(filepath=base_path + texture_file)
    links.new(tex_image_node.outputs['Color'], bsdf_node.inputs['Base Color'])

    # 绑定材质到对象
    obj.data.materials.append(mat)

# 计算每个循环的总帧数
num_objects = len(loaded_objects)
cycle_frames = num_objects * frame_step * 2  # 正序和倒序

# 计算需要的循环次数
num_cycles = frame_end // cycle_frames + 1

# 循环插入关键帧
current_frame = frame_start
for cycle in range(num_cycles):
    # 正序
    for i, obj in enumerate(loaded_objects):
        # 隐藏所有对象
        for other_obj in loaded_objects:
            other_obj.hide_render = True
            other_obj.hide_viewport = True
            other_obj.keyframe_insert(data_path="hide_render", frame=current_frame)
            other_obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        
        # 显示当前对象
        obj.hide_render = False
        obj.hide_viewport = False
        obj.keyframe_insert(data_path="hide_render", frame=current_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        
        # 保持显示直到下一个对象
        current_frame += frame_step
        obj.keyframe_insert(data_path="hide_render", frame=current_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
    
    # 倒序
    for i, obj in enumerate(reversed(loaded_objects)):
        # 隐藏所有对象
        for other_obj in loaded_objects:
            other_obj.hide_render = True
            other_obj.hide_viewport = True
            other_obj.keyframe_insert(data_path="hide_render", frame=current_frame)
            other_obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        
        # 显示当前对象
        obj.hide_render = False
        obj.hide_viewport = False
        obj.keyframe_insert(data_path="hide_render", frame=current_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
        
        # 保持显示直到下一个对象
        current_frame += frame_step
        obj.keyframe_insert(data_path="hide_render", frame=current_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)

    # 检查是否超过总帧数
    if current_frame > frame_end:
        break

# 设置帧范围
bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = frame_end

# 设置相机
camera_data = bpy.data.cameras.new(name="Camera")
camera_object = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
bpy.context.scene.camera = camera_object
camera_object.location = (0, -15, 11)
camera_object.rotation_euler = (math.radians(63), 0, 0)  # 将1.1弧度转换为度
camera_data.lens = 20

# 创建空对象作为摄像机的父对象
empty = bpy.data.objects.new("Empty", None)
bpy.context.collection.objects.link(empty)
camera_object.parent = empty

# 设置摄像机环绕动画
for frame in range(frame_start, frame_end + 1):
    bpy.context.scene.frame_set(frame)
    angle = (frame - frame_start) * (2 * math.pi / frame_end)
    empty.rotation_euler = (0, 0, angle)
    empty.keyframe_insert(data_path="rotation_euler", index=-1)

# 设置渲染输出路径和格式
bpy.context.scene.render.filepath = base_path + "animation.mp4"
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'

# 渲染动画
bpy.ops.render.render(animation=True)