from PIL import Image, ImageFilter
import numpy as np

# 读取图片并转换为RGBA
image_path = r"C:\Users\Philips Deng\Documents\GitHub\Scriptsfor24WS\data\deer_ablation\render_still_15.png"  # 替换为你的图片路径
image = Image.open(image_path).convert("RGBA")

# 轻微模糊处理，减少边缘锯齿
image = image.filter(ImageFilter.GaussianBlur(radius=3))

# 转换为 NumPy 数组
img_array = np.array(image)

# 黑色像素范围（允许一些偏差，比如0-30的黑色）
black_threshold = 50  # 允许0-30之间的灰度值都算黑色
white_color = np.array([255, 255, 255, 255])  # 纯白色（RGBA）

# 找到接近黑色的像素
mask = (img_array[:, :, 0] <= black_threshold) & \
       (img_array[:, :, 1] <= black_threshold) & \
       (img_array[:, :, 2] <= black_threshold)

# 替换黑色像素为白色
img_array[mask] = white_color

# 转换回 PIL 图像
new_image = Image.fromarray(img_array)


new_image.save(image_path)
new_image.show()

