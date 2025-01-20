from diffusers import FluxPipeline
import torch

ckpt_id = "black-forest-labs/FLUX.1-schnell"
prompt = [
    "an astronaut riding a horse",
    # more prompts here
]
height, width = 1024, 1024

# denoising
pipe = FluxPipeline.from_pretrained(
    ckpt_id,
    torch_dtype=torch.bfloat16,
)
pipe.vae.enable_tiling()
pipe.vae.enable_slicing()
pipe.enable_sequential_cpu_offload() # offloads modules to CPU on a submodule level (rather than model level)

image = pipe(
    prompt,
    num_inference_steps=1,
    guidance_scale=0.0,
    height=height,
    width=width,
).images[0]
print('Max mem allocated (GB) while denoising:', torch.cuda.max_memory_allocated() / (1024 ** 3))

import matplotlib.pyplot as plt
plt.imshow(image)
plt.show()