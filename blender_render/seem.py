import bpy
import bmesh
from math import radians
from PIL import Image, ImageFilter
import os

# Assume the mesh object is selected
obj = bpy.context.object

# Enter edit mode
bpy.ops.object.mode_set(mode='EDIT')

# Get the BMesh representation of the mesh
bm = bmesh.from_edit_mesh(obj.data)

# Clear existing seams
for edge in bm.edges:
    edge.seam = False

# Select sharp edges (angle > 30 degrees) and mark as seams
for edge in bm.edges:
    if edge.calc_face_angle() > radians(30):
        edge.select = True

# Mark selected edges as seams
bpy.ops.mesh.mark_seam()

# Select all faces for unwrapping
bpy.ops.mesh.select_all(action='SELECT')

# Unwrap the model using the angle-based method
bpy.ops.uv.unwrap(method='ANGLE_BASED')

# Pack UV islands to optimize space
bpy.ops.uv.pack_islands()

# Exit edit mode
bpy.ops.object.mode_set(mode='OBJECT')

# Export UV layout as a wireframe image
uv_path = 'uv_wireframe.png'
bpy.ops.uv.export_layout(filepath=uv_path, size=(1024, 1024), opacity=1.0)

# Define paths for texture processing
texture_path = 'texture.png'  # Replace with your texture file path
blended_texture_path = 'texture_blended.png'

# Load UV wireframe image and convert to grayscale
uv_wireframe = Image.open(uv_path).convert('L')

# Dilate UV edges to create a seam mask
seam_mask = uv_wireframe.filter(ImageFilter.MaxFilter(5))

# Load the original texture
texture = Image.open(texture_path)

# Create a blurred version of the texture
blurred_texture = texture.filter(ImageFilter.GaussianBlur(5))

# Prepare the seam mask for compositing (convert to binary)
seam_mask = seam_mask.point(lambda p: 255 if p > 0 else 0)

# Composite the blurred texture with the original using the seam mask
result = Image.composite(blurred_texture, texture, seam_mask)

# Save the blended texture
result.save(blended_texture_path)

# Update the material with the blended texture
mat = obj.data.materials[0]  # Assume the first material slot
for node in mat.node_tree.nodes:
    if node.type == 'TEX_IMAGE':
        node.image = bpy.data.images.load(blended_texture_path)
        break

print("Texture seams processed successfully!")