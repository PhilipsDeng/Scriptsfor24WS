import torch
from diffusers import FluxControlPipeline, FluxTransformer2DModel
from diffusers.utils import load_image
from image_gen_aux import DepthPreprocessor

pipe = FluxControlPipeline.from_pretrained("black-forest-labs/FLUX.1-Depth-dev", torch_dtype=torch.bfloat16).to("cuda")

prompt = "Philips Deng"
control_image = load_image("data/00009.png")

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
image.save("output.png")