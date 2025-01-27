import torch
from diffusers import FluxControlPipeline, FluxTransformer2DModel
from diffusers.utils import load_image
from image_gen_aux import DepthPreprocessor

pipe = FluxControlPipeline.from_pretrained("black-forest-labs/FLUX.1-Depth-dev", torch_dtype=torch.bfloat16).to("cuda")

prompt = "A beautiful highly-detailed pink dragon with a long tail and large wings flying in front of a Barbie castle in the Barbie movie, the weather is sunny and the sky is clear."
control_image = load_image("data/00000.png")

# processor = DepthPreprocessor.from_pretrained("LiheYoung/depth-anything-large-hf")
# control_image = processor(control_image)[0].convert("RGB")

image = pipe(
    prompt=prompt,
    control_image=control_image,
    height=1024,
    width=1024,
    num_inference_steps=30,
    guidance_scale=10.0,
    generator=torch.Generator().manual_seed(42),
).images[0]
image.save("output.png")