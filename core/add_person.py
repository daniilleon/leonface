# core/add_person.py

import face_recognition
import numpy as np
import logging
from core.db import insert_person, insert_photo, get_all_photos
from core.utils import compress_image, convert_heic_to_jpg, is_supported_image

def is_face_already_registered(face_encoding):
    photos = get_all_photos()
    for person in photos:
        db_encoding = np.frombuffer(person[7], dtype=np.float64)
        if face_recognition.compare_faces([db_encoding], face_encoding)[0]:
            return person
    return None

def add_person_interactive(image_path):
    try:
        print(f"[DEBUG] Проверяем изображение: {image_path}")
        if not is_supported_image(image_path):
            print("❌ Неподдерживаемый формат изображения.")
            return

        if image_path.lower().endswith(".heic"):
            image_path = convert_heic_to_jpg(image_path)

        image_path = compress_image(image_path)
        print(f"[DEBUG] Сжатое изображение: {image_path}")

        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            print("❌ Лицо не найдено на изображении.")
            return

        face_encoding = face_encodings[0]
        print(f"[DEBUG] Вектор получен, длина: {len(face_encoding)}")

        existing = is_face_already_registered(face_encoding)
        if existing:
            print("⚠️ Это лицо уже есть в базе.")
            print(f"Имя: {existing[1]} {existing[2]}, логин: {existing[3]}")
            return

        print("✅ Лицо не найдено в базе. Можно добавить нового пользователя.")

        # Запрашиваем ввод данных
        first_name = input("Имя: ")
        last_name = input("Фамилия: ")
        username = input("Логин: ")
        phone = input("Телефон: ")
        telegram = input("Telegram (без @): ")
        whatsapp = input("WhatsApp (без https://wa.me/): ")

        with open(image_path, "rb") as f:
            photo_blob = f.read()

        person_id = insert_person(
            first_name,
            last_name,
            username,
            phone,
            telegram,
            whatsapp
        )
        insert_photo(person_id, photo_blob, face_encoding)

        print(f"✅ Пользователь {first_name} {last_name} успешно добавлен (ID {person_id})")

    except Exception as e:
        print(f"❌ Ошибка при добавлении: {e}")
        logging.error(f"Ошибка: {e}", exc_info=True)

def add_person_by_data(image_path, first_name, last_name, username, phone, telegram, whatsapp):
    # Этот метод используется в боте
    try:
        if not is_supported_image(image_path):
            return "❌ Неподдерживаемый формат изображения."

        if image_path.lower().endswith(".heic"):
            image_path = convert_heic_to_jpg(image_path)

        image_path = compress_image(image_path)
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            return "❌ Лицо не найдено на изображении."

        face_encoding = face_encodings[0]
        existing = is_face_already_registered(face_encoding)
        if existing:
            return f"⚠️ Это лицо уже есть в базе: {existing[1]} {existing[2]} (логин: {existing[3]})"

        with open(image_path, "rb") as f:
            photo_blob = f.read()

        person_id = insert_person(first_name, last_name, username, phone, telegram, whatsapp)
        insert_photo(person_id, photo_blob, face_encoding)

        return f"✅ Пользователь {first_name} {last_name} успешно добавлен."

    except Exception as e:
        logging.error(f"Ошибка при добавлении: {e}", exc_info=True)
        return f"❌ Ошибка при добавлении: {e}"
