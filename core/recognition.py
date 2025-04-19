import face_recognition
import numpy as np
import logging
from core.db import get_all_photos
from core.utils import convert_heic_to_jpg, compress_image, is_supported_image

def recognize_faces_from_image(image_path):
    try:
        # HEIC → JPG, если нужно
        if image_path.lower().endswith(".heic"):
            image_path = convert_heic_to_jpg(image_path)

        # Сжимаем изображение
        image_path = compress_image(image_path)

        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            return ["❌ Лица не найдены на изображении."]

        photos = get_all_photos()
        results = []

        for i, face_encoding in enumerate(face_encodings):
            matched = False
            for person in photos:
                db_encoding = np.frombuffer(person[7], dtype=np.float64)
                match = face_recognition.compare_faces([db_encoding], face_encoding)

                if match[0]:
                    result = (
                        f"👤 Лицо #{i + 1}:\n"
                        f"ФИО: {person[1]} {person[2]}\n"
                        f"Логин: {person[3]}\n"
                        f"Телефон: {person[4]}\n"
                        f"Telegram: {person[5]}\n"
                        f"WhatsApp: {person[6]}"
                    )
                    results.append(result)
                    matched = True
                    break

            if not matched:
                results.append(f"👤 Лицо #{i + 1}: ❌ Человек не найден.")

        return results

    except Exception as e:
        logging.error(f"Ошибка при распознавании: {e}")
        return [f"❌ Ошибка: {e}"]