from PIL import Image
import numpy as np
import os

def extract_channels(base_path):

    input_path = os.path.join(base_path, "texture_ks.png")
    
    if not os.path.exists(input_path):
        print(f"Not found: {input_path}")
        return

    image = Image.open(input_path).convert('RGB')
    
    img_array = np.array(image)
    
    metallic = img_array[:, :, 2]
    roughness = img_array[:, :, 1]
    
    metallic_path = os.path.join(base_path, "texture_metallic.png")
    roughness_path = os.path.join(base_path, "texture_roughness.png")

    Image.fromarray(metallic).save(metallic_path)
    Image.fromarray(roughness).save(roughness_path)
    
    print("Extraction finished: texture_metallic.png & texture_roughness.png")

if __name__ == "__main__":
    extract_channels("/home/philipsdeng/文档/GitHub/Scriptsfor24WS/data/dragonOLO_act17/")
