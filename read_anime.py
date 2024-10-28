import struct
import numpy as np

def load_anime_file(filepath):
    with open(filepath, "rb") as file:
        # Step 1: Read nf, nv, nt
        nf = struct.unpack("i", file.read(4))[0]
        nv = struct.unpack("i", file.read(4))[0]
        nt = struct.unpack("i", file.read(4))[0]

        # Step 2: Read vertex data of the first frame
        vertices = np.frombuffer(file.read(nv * 3 * 4), dtype=np.float32).reshape((nv, 3))

        # Read triangle face data of the first frame
        triangles = np.frombuffer(file.read(nt * 3 * 4), dtype=np.int32).reshape((nt, 3))

        # Store all frames
        frames = [vertices.copy()]

        # Step 3: Read 3D offset data from the 2nd to the last frame
        for _ in range(1, nf):
            offsets = np.frombuffer(file.read(nv * 3 * 4), dtype=np.float32).reshape((nv, 3))
            new_frame = frames[0] + offsets
            frames.append(new_frame)

    return frames, triangles

# Example usage:
frames, triangles = load_anime_file("bear3EP_Agression.anime")
print("Number of frames:", len(frames))
print("First frame vertices:\n", frames[0])
print("First frame triangles:\n", triangles)
