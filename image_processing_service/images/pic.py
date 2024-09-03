from PIL import Image
from rembg import remove
from django.core.files.storage import default_storage

def save_new (image):
        file_name = default_storage.save(f'images/{image.id}', image)
        file_url = default_storage.url(file_name)

def resize_image(image_path, size):
    image = Image.open(image_path)
    resized_image = image.resize(size)
    return resized_image
def crop_image(image_path, box):
    image = Image.open(image_path)
    cropped_image = image.crop(box)
    return cropped_image
def rotate_image(image_path, angle):
    image = Image.open(image_path)
    rotated_image = image.rotate(angle)
    return rotated_image
def flip_image(image_path, direction):
    image = Image.open(image_path)
    if direction == 'horizontal':
        flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)
    elif direction == 'vertical':
        flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
    else:
        raise ValueError("Direction must be 'horizontal' or 'vertical'")
    return flipped_image
def mirror_image(image_path):
    image = Image.open(image_path)
    mirrored_image = image.transpose(Image.FLIP_LEFT_RIGHT)
    return mirrored_image
def compress_image(image_path, output_path, quality=85):
    image = Image.open(image_path)
    image.save(output_path, quality=quality)
def change_format(image_path, output_path, format):
    image = Image.open(image_path)
    image.save(output_path, format=format)
def apply_sepia(image_path):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    pixels = image.load()  # Create the pixel map
    
    for py in range(height):
        for px in range(width):
            r, g, b = image.getpixel((px, py))
            
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            
            if tr > 255:
                tr = 255

            if tg > 255:
                tg = 255

            if tb > 255:
                tb = 255

            pixels[px, py] = (tr, tg, tb)

    return image

def remove_background_deep_learning(image_path, output_path):
    input_image = Image.open(image_path)
    output_image = remove(input_image)
    output_image.save(output_path)
