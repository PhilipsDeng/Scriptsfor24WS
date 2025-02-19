import torch
from diffusers import FluxControlPipeline, FluxTransformer2DModel
from diffusers.utils import load_image
# from image_gen_aux import DepthPreprocessor
import os

cache_path = "/root/autodl-tmp/.cache/huggingface/hub"
os.makedirs(cache_path, exist_ok=True)
pipe = FluxControlPipeline.from_pretrained("black-forest-labs/FLUX.1-Depth-dev", torch_dtype=torch.float8_e4m3fn, cache_dir=cache_path).to("cuda")


prompt = "one dragon from lord of the rings"
control_image = load_image("Github/Scriptsfor24WS/data/depth_img/00009.png")

# processor = DepthPreprocessor.from_pretrained("LiheYoung/depth-anything-large-hf")
# control_image = processor(control_image)[0].convert("RGB")

image = pipe(
    prompt=prompt,
    control_image=control_image,
    height=1024,
    width=1024,
    num_inference_steps=40,
    guidance_scale=10.0,
    generator=torch.Generator().manual_seed(328),
).images[0]

image.save("Github/Scriptsfor24WS/data/outputs/FLUX_depth_fp16.png")

from PIL import Image

# 假设 control_image 和 image 都是 PIL Image 对象
# 获取两幅图像的尺寸
width1, height1 = control_image.size
width2, height2 = image.size

# 创建一个新的空白图像，其宽度为两幅图像宽度之和，高度为两者中较大的那个
combined_width = width1 + width2
combined_height = max(height1, height2)
combined_image = Image.new('RGB', (combined_width, combined_height))

# 将 control_image 粘贴到左边
combined_image.paste(control_image, (0, 0))

# 将 image 粘贴到右边，位置起点为 (width1, 0)
combined_image.paste(image, (width1, 0))

# 保存合并后的图像
combined_image.save("Github/Scriptsfor24WS/data/outputs/combined_image.png")
