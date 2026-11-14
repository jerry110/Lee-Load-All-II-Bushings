import subprocess
import os
import sys

SCAD_FILE = "lee_bushing.scad"
IMAGE_DIR = "bushing_images"

# Numbers to generate images for (change to range(1, 201) if you want images for ALL 200)
NUMBERS_TO_RENDER = [1, 25, 50, 75, 100, 125, 150, 175, 200]

def get_openscad_path():
    if sys.platform.startswith("win"):
        default_path = r"C:\Program Files\OpenSCAD\openscad.exe"
        return default_path if os.path.exists(default_path) else "openscad"
    return "openscad"

openscad_bin = get_openscad_path()

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

print(f"Generating preview PNG images in '{IMAGE_DIR}/'...")

for i in NUMBERS_TO_RENDER:
    num_str = f"{i:03d}"
    img_filename = os.path.join(IMAGE_DIR, f"Lee_Bushing_{num_str}.png")
    
    cmd = [
        openscad_bin,
        "-o", img_filename,
        "-D", f"bushing_number={i}",
        "--imgsize=1024,1024",           # 1024x1024 square images (ideal for Printables/Thingiverse)
        "--colorscheme=Tomorrow Night",  # Clean dark theme (or try "Cornfield" / "Sunset")
        "--camera=0,-50,30,0,0,6,0",     # Positions camera to frame the front text and top bore clearly
        SCAD_FILE
    ]
    
    print(f"Rendering image [{num_str}] -> {img_filename}")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"\nDone! Previews saved to the '{IMAGE_DIR}' folder.")
