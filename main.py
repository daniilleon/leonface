from core.add_photo_to_person import add_photo_to_person_by_username
from core.log_formatter import setup_logging
setup_logging()

from core.add_person import add_person_interactive
from core.recognition import recognize_faces_from_image
from core.recognize_video import recognize_faces_on_video
import face_recognition_models  # Необязательно импортировать явно
import face_recognition


def main():
    print("1. Добавить человека")
    print("2. Распознать людей по фото")
    print("3. Распознать людей на видео")
    print("4. Добавить фото к пользователю")
    print("5. Редактировать профиль пользователя")

    choice = input("Выберите опцию: ")

    if choice == "1":
        image_path = input("Путь к фотографии: ").strip()
        add_person_interactive(image_path)

    # elif choice == "2":
    #     image_path = input("Путь к фотографии для распознавания: ").strip()
    #     recognize_faces_from_image(image_path)

    elif choice == "2":
        image_path = input("Путь к фотографии для распознавания: ").strip()
        results = recognize_faces_from_image(image_path)
        for res in results:
            print(res)


    # elif choice == "3":
    #     video_path = input("Путь к видео для распознавания: ").strip()
    #     recognize_faces_on_video(video_path)
    elif choice == "3":
        video_path = input("Путь к видео для распознавания: ").strip()
        results = recognize_faces_on_video(video_path)
        print("\n📋 Результаты распознавания:")
        for res in results:
            print(res)

    elif choice == "4":
        username = input("Введите логин пользователя: ").strip()
        image_path = input("Путь к фотографии: ").strip()
        add_photo_to_person_by_username(username, image_path)

    elif choice == "5":
        from core.edit_person import edit_person_by_username
        edit_person_by_username()



if __name__ == "__main__":
    main()