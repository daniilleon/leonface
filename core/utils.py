import os
from PIL import Image
import pillow_heif

def convert_heic_to_jpg(heic_path):
    """Конвертирует HEIC-фото в JPG (через pillow-heif)"""
    pillow_heif.register_heif_opener()
    image = Image.open(heic_path)
    new_path = os.path.splitext(heic_path)[0] + ".jpg"
    image.save(new_path, format="JPEG")
    return new_path

def compress_image(image_path, max_size_kb=1024):
    """Сжимает изображение и сохраняет как JPEG"""
    image = Image.open(image_path)

    # Конвертируем RGBA → RGB, чтобы избежать ошибок
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    image_format = image.format
    temp_path = os.path.splitext(image_path)[0] + "_compressed.jpg"

    image.save(temp_path, format="JPEG", quality=70, optimize=True)

    # Проверка размера и повторное сжатие, если надо
    if os.path.getsize(temp_path) > max_size_kb * 1024:
        image.save(temp_path, format="JPEG", quality=50, optimize=True)

    return temp_path


def is_supported_image(file_path):
    """Проверяет, поддерживается ли формат изображения"""
    supported = ('.jpg', '.jpeg', '.png', '.heic')
    return file_path.lower().endswith(supported)
