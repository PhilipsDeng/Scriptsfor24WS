import bpy
import math
from tqdm import tqdm

# 文件路径
obj_file_path = r"C:\Users\Philips Deng\Desktop\dragon\dragon_stand\dragon.obj"  # 替换为你的 obj 文件路径
texture_file_path = r"C:\Users\Philips Deng\Desktop\dragon\dragon_stand\red.png"  # 替换为你的贴图文件路径
output_image_path = r"C:\Users\Philips Deng\Desktop\dragon\dragon_stand\preview.png"  # 预览图像路径
output_video_path = r"C:\Users\Philips Deng\Desktop\dragon\dragon_stand\output.mp4"  # 最终视频输出路径

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
bpy.ops.object.camera_add(location=(5, -5, 3.5))
camera = bpy.context.object
camera.rotation_euler = (1.21, 0, 0.785)  # 初始旋转

# 设置场景的相机
bpy.context.scene.camera = camera

# 添加灯光
bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
point_light = bpy.context.object
point_light.data.energy = 5000 
point_light.data.shadow_soft_size = 0.1
point_light.data.size = 1000
point_light.location = (0, 0, 5)
point_light.rotation_euler = (math.radians(0), math.radians(0), math.radians(0))

# 创建一个空物体用于摄像机环绕
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
empty = bpy.context.object

# 使摄像机跟随空物体
camera.parent = empty

# 设置摄像机环绕动画
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250
for frame in tqdm(range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1), desc="设置摄像机环绕动画进度"):
    bpy.context.scene.frame_set(frame)
    angle = frame * (2 * math.pi / bpy.context.scene.frame_end)
    empty.rotation_euler = (0, 0, angle)
    empty.keyframe_insert(data_path="rotation_euler", index=-1)

# 只渲染一帧用于预览
bpy.context.scene.render.filepath = output_image_path  # 设置输出文件路径
bpy.context.scene.frame_set(1)  # 选择第一帧进行渲染
bpy.ops.render.render(write_still=True)  # 渲染当前帧并保存

# 渲染完成后自动打开输出的图片
if os.path.exists(output_image_path):
    try:
        if os.name == 'nt':  # Windows
            os.startfile(output_image_path)
        elif os.name == 'posix':  # macOS or Linux
            subprocess.call(['open', output_image_path] if sys.platform == 'darwin' else ['xdg-open', output_image_path])
    except Exception as e:
        print(f"打开图片时发生错误：{e}")

print("预览图像已保存。请检查预览图像是否符合要求，再决定是否继续渲染。")

# 检查用户输入来决定是否继续渲染
user_input = input("请输入 'yes' 继续渲染，或输入 'no' 取消: ")

if user_input.lower() == 'yes':
    # 设置渲染视频的参数
    bpy.context.scene.render.filepath = output_video_path
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    bpy.context.scene.render.ffmpeg.ffmpeg_preset = 'GOOD'

    print("开始渲染动画...")
    for _ in tqdm(range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1), desc="渲染动画进度"):
        bpy.ops.render.render(animation=True)
    print("渲染完成！")

