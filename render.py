import bpy
import math
import os

# Blender --background --python render.py

# 从文件中读取路径
paths_file = r"C:\Users\phili\Documents\Github\Scriptsfor24WS\path.txt"  # 存储路径的文件路径

# 读取路径文件内容
def read_paths(file_path):
    paths = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            paths[key.strip()] = value.strip()
    return paths

# 获取路径
paths = read_paths(paths_file)
obj_file_path = paths.get('obj_file_path')
texture_file_path = paths.get('texture_file_path')
output_image_path = paths.get('output_image_path')
output_video_path = paths.get('output_video_path')

# 删除默认的立方体
if "Cube" in bpy.data.objects:
    bpy.data.objects["Cube"].select_set(True)
    bpy.ops.object.delete()

# 导入OBJ文件
bpy.ops.wm.obj_import(filepath=obj_file_path)
obj = bpy.context.selected_objects[0]

# 调整龙的大小
obj.scale = (0.5, 0.5, 0.5)  # 缩小龙的大小，按需修改比例

# 创建材质并应用贴图
material = bpy.data.materials.new(name="ObjMaterial")
material.use_nodes = True
obj.data.materials.append(material)

# 获取材质节点
nodes = material.node_tree.nodes
links = material.node_tree.links

# 清空默认节点
for node in nodes:
    nodes.remove(node)

# 设置材质和贴图
bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
output_node = nodes.new(type='ShaderNodeOutputMaterial')
texture_node = nodes.new(type='ShaderNodeTexImage')
texture_node.image = bpy.data.images.load(texture_file_path)

# 连接节点
links.new(texture_node.outputs['Color'], bsdf_node.inputs['Base Color'])
links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

# 添加并设置摄像机
bpy.ops.object.camera_add(location=(5, -5, 3))
camera = bpy.context.object
camera.rotation_euler = (1.109, 0, 0.785)  # 初始旋转

# 设置场景的相机
bpy.context.scene.camera = camera

# 添加灯光
bpy.ops.object.light_add(type='SUN', location=(10, -10, 10))
sun_light = bpy.context.object
sun_light.data.energy = 5  # 调整灯光强度

bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
point_light = bpy.context.object
point_light.data.energy = 300  # 增加一个点光源用于更好地照亮龙

# 创建一个空物体用于摄像机环绕
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
empty = bpy.context.object

# 使摄像机跟随空物体
camera.parent = empty

# 设置摄像机环绕动画
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250
for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
    bpy.context.scene.frame_set(frame)
    angle = frame * (2 * math.pi / bpy.context.scene.frame_end)
    empty.rotation_euler = (0, 0, angle)
    empty.keyframe_insert(data_path="rotation_euler", index=-1)

# 只渲染一帧用于预览
bpy.context.scene.render.filepath = output_image_path  # 设置输出文件路径
bpy.context.scene.frame_set(1)  # 选择第一帧进行渲染
bpy.ops.render.render(write_still=True)  # 渲染当前帧并保存

print("预览图像已保存。请检查预览图像是否符合要求，再决定是否继续渲染。")

# 检查用户输入来决定是否继续渲染
user_input = input("请输入 'yes' 继续渲染，或输入 'no' 取消: ")

if user_input.lower() == 'yes':
    # 继续渲染完整动画
    bpy.context.scene.render.filepath = output_video_path
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'GOOD'

    print("开始渲染动画...")
    bpy.ops.render.render(animation=True)
    print("渲染完成！")
else:
    print("渲染已取消。")
