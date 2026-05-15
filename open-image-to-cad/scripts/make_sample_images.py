from PIL import Image, ImageDraw
import os

os.makedirs("examples/sample_inputs", exist_ok=True)

# Create a simple plate image
img = Image.new('RGB', (400, 200), color = 'white')
d = ImageDraw.Draw(img)

# Draw plate outline
d.rectangle([50, 50, 350, 150], outline="black", width=3)

# Draw holes
d.ellipse([100-15, 100-15, 100+15, 100+15], outline="black", width=2)
d.ellipse([300-15, 100-15, 300+15, 100+15], outline="black", width=2)

img.save("examples/sample_inputs/simple_plate.png")

with open("examples/sample_inputs/simple_plate.svg", "w") as f:
    f.write("""<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect x="50" y="50" width="300" height="100" stroke="black" stroke-width="3" fill="none" />
  <circle cx="100" cy="100" r="15" stroke="black" stroke-width="2" fill="none" />
  <circle cx="300" cy="100" r="15" stroke="black" stroke-width="2" fill="none" />
</svg>""")

print("Sample inputs generated.")
