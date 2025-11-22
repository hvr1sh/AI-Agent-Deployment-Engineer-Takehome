import base64
from io import BytesIO
from PIL import Image

def save_base64_image(b64_str, filename="image.png"):
    """Save base64 image to file"""
    image_bytes = base64.b64decode(b64_str)
    with open(filename, "wb") as f:
        f.write(image_bytes)
    return filename

def base64_to_image(b64_str):
    """Convert base64 string to PIL Image"""
    image_bytes = base64.b64decode(b64_str)
    return Image.open(BytesIO(image_bytes))

def generate_single_image(args):
    """Helper function to generate a single image (for parallel processing)"""
    section, index, model, img_size = args
    img_b64 = model.generate_image_from_text(section, size=img_size)
    save_base64_image(img_b64, f"{index}.png")
    return index, img_b64