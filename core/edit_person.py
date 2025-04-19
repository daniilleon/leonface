# core/edit_person.py

import logging
from core.db import get_person_by_username_full, update_person

def edit_person_by_username():
    username = input("Введите логин пользователя для редактирования: ").strip()
    person = get_person_by_username_full(username)

    if not person:
        print("❌ Пользователь не найден.")
        return

    print(f"👤 Текущие данные:\n"
          f"Имя: {person[1]}\n"
          f"Фамилия: {person[2]}\n"
          f"Телефон: {person[4]}\n"
          f"Telegram: {person[5]}\n"
          f"WhatsApp: {person[6]}\n")

    new_first_name = input(f"Новое имя (оставь пустым чтобы не менять): ").strip() or person[1]
    new_last_name = input(f"Новая фамилия (оставь пустым): ").strip() or person[2]
    new_phone = input(f"Новый телефон (оставь пустым): ").strip() or person[4]
    new_telegram = input(f"Новый Telegram (без @, оставь пустым): ").strip() or person[5].lstrip('@')
    new_whatsapp = input(f"Новый WhatsApp (только номер, оставь пустым): ").strip() or person[6].removeprefix("https://wa.me/")

    update_person(
        username=username,
        first_name=new_first_name,
        last_name=new_last_name,
        phone=new_phone,
        telegram=new_telegram,
        whatsapp=new_whatsapp
    )

    print("✅ Данные пользователя обновлены.")
    logging.info(f"📝 Пользователь {username} отредактирован.")
