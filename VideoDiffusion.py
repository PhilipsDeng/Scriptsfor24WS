import torch
from diffusers.utils import load_image, export_to_gif
from diffusers import I2VGenXLPipeline
from PIL import Image


def bytes_to_giga_bytes(bytes):
    return f"{(bytes / 1024 / 1024 / 1024):.3f}"

pipeline = I2VGenXLPipeline.from_pretrained("ali-vilab/i2vgen-xl", torch_dtype=torch.float16, variant="fp16")
pipeline.enable_model_cpu_offload()

image_url ="https://huggingface.co/datasets/diffusers/docs-images/resolve/main/i2vgen_xl_images/img_0009.png"
image = load_image(image_url).convert("RGB")

width, height = image.size
image = image.resize((width // 2, height // 2), Image.LANCZOS)

prompt = "Papers were floating in the air on a table in the library"
negative_prompt = "Distorted, discontinuous, Ugly, blurry, low resolution, motionless, static, disfigured, disconnected limbs, Ugly faces, incomplete arms"
generator = torch.manual_seed(8888)

frames = pipeline(
    prompt=prompt,
    image=image,
    negative_prompt=negative_prompt,
    generator=generator
).frames[0]
video_path = export_to_gif(frames, "i2v.gif")

memory = bytes_to_giga_bytes(torch.cuda.max_memory_allocated())
print(f"Memory: {memory}GB")