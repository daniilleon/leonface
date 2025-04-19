import face_recognition
import numpy as np
import logging
from core.db import get_person_by_username, insert_photo
from core.utils import compress_image, convert_heic_to_jpg, is_supported_image

def add_photo_to_person_by_username(username, image_path):
    try:
        person = get_person_by_username(username)
        if not person:
            print(f"❌ Пользователь с логином '{username}' не найден.")
            return

        person_id = person[0]

        if not is_supported_image(image_path):
            print("❌ Неподдерживаемый формат изображения.")
            return

        if image_path.lower().endswith(".heic"):
            image_path = convert_heic_to_jpg(image_path)

        image_path = compress_image(image_path)

        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            print("❌ Лицо не найдено на изображении.")
            return

        face_encoding = face_encodings[0]

        with open(image_path, "rb") as f:
            photo_blob = f.read()

        insert_photo(person_id, photo_blob, face_encoding)
        print(f"✅ Фото добавлено к пользователю '{username}'.")
        logging.info(f"Новое фото для пользователя {username} успешно добавлено")

    except Exception as e:
        logging.error(f"Ошибка при добавлении фото: {e}")
        print(f"❌ Ошибка: {e}")
