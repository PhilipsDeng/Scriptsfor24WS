import torch
from diffusers import FluxTransformer2DModel, FluxControlPipeline
from diffusers.utils import load_image
from transformers import T5EncoderModel, CLIPTextModel
from optimum.quanto import freeze, qfloat8, quantize
import os

device = "cuda:0" if torch.cuda.is_available() else "cpu"
cache_path = "/root/autodl-tmp/.cache/huggingface/hub"
os.makedirs(cache_path, exist_ok=True)


bfl_repo = "black-forest-labs/FLUX.1-Depth-dev"
dtype = torch.bfloat16

print("loading transformer")
transformer = FluxTransformer2DModel.from_single_file("/root/autodl-tmp/.cache/huggingface/hub/models--boricuapab--flux1-depth-dev-fp8/snapshots/e88c032dcb759924635956bdbfee5362e1f5c0fe/flux1-depth-dev-fp8.safetensors", torch_dtype=dtype, cache_dir=cache_path).to(device)

quantize(transformer, weights=qfloat8)
freeze(transformer)

print("loading text_encoder")
text_encoder_2 = T5EncoderModel.from_pretrained(bfl_repo, subfolder="text_encoder_2", torch_dtype=dtype, cache_dir=cache_path).to(device)
quantize(text_encoder_2, weights=qfloat8)
freeze(text_encoder_2)

print("loading pipe")
pipe = FluxControlPipeline.from_pretrained(bfl_repo, transformer=None, text_encoder_2=None, torch_dtype=dtype, cache_dir=cache_path).to(device)

pipe.transformer = transformer.to(device)
pipe.text_encoder_2 = text_encoder_2.to(device)

pipe.enable_model_cpu_offload()

prompt = "A cat holding a sign that says hello world"
control_image = load_image("/root/autodl-tmp/Github/Scriptsfor24WS/data/depth_img/00009.png")

print("diffusing...")
image = pipe(
    prompt=prompt,
    control_image=control_image,
    height=1024,
    width=1024,
    num_inference_steps=20,
    guidance_scale=3.5,
    generator=torch.Generator().manual_seed(328),
).images[0]

image.save("/root/autodl-tmp/Github/Scriptsfor24WS/data/outputs/FLUX_depth_fp16.png")