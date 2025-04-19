import cv2
import dlib
import numpy as np
from core.db import get_all_photos

# Подгружаем модель лиц и landmarks
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
face_encoder = dlib.face_recognition_model_v1("models/dlib_face_recognition_resnet_model_v1.dat")

def recognize_faces_on_video(video_path):
    video_capture = cv2.VideoCapture(video_path)
    photos = get_all_photos()

    results = []
    recognized_names = set()

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = detector(rgb_frame)

        for i, face in enumerate(faces):
            shape = predictor(rgb_frame, face)
            face_descriptor = face_encoder.compute_face_descriptor(rgb_frame, shape)
            encoding = np.array(face_descriptor)

            name = "Неизвестно"
            for person in photos:
                try:
                    db_encoding = np.frombuffer(person[7], dtype=np.float64)
                    match = np.linalg.norm(db_encoding - encoding) < 0.6
                except Exception as e:
                    print(f"[ERROR] Ошибка при сравнении лиц: {e}")
                    continue

                if match:
                    name = f"{person[1]} {person[2]}"
                    if name not in recognized_names:
                        result = (
                            f"\n👤 Лицо #{i + 1}:\n"
                            f"ФИО: {person[1]} {person[2]}\n"
                            f"Логин: {person[3]}\n"
                            f"Телефон: {person[4]}\n"
                            f"Telegram: {person[5]}\n"
                            f"WhatsApp: {person[6]}"
                        )
                        results.append(result)
                        recognized_names.add(name)
                    break

            # Отображаем лицо на экране
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Распознавание на видео (dlib)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return results
