from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.loader import bot
from bot.fsm.states import MediaState, AddUserStates, AddPhotoStates
from core.recognition import recognize_faces_from_image
from core.add_person import add_person_by_data
from core.add_photo_to_person import add_photo_to_person_by_username
from bot.config import DOWNLOAD_DIR, ADMIN_IDS
import os
import uuid

router = Router()

@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    state_data = await state.get_state()

    # 📂 Создаём уникальный путь к файлу
    file = await bot.get_file(message.photo[-1].file_id)
    unique_filename = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(DOWNLOAD_DIR, unique_filename)
    await bot.download_file(file.file_path, destination=file_path)

    try:
        # --- Добавление профиля (для админа) ---
        if state_data == AddUserStates.waiting_for_photo.state:
            if user_id not in ADMIN_IDS:
                await message.answer("❌ У вас нет прав для этой операции.")
                return

            await state.update_data(photo_path=file_path)
            await state.set_state(AddUserStates.waiting_for_first_name)
            await message.answer("Введите имя пользователя:")
            return

        # --- Добавление дополнительного фото ---
        if state_data == AddPhotoStates.waiting_for_photo.state:
            if user_id not in ADMIN_IDS:
                await message.answer("❌ У вас нет прав для этой операции.")
                return

            data = await state.get_data()
            username = data.get("username")

            await message.answer("📷 Обрабатываю и добавляю фото...")
            try:
                add_photo_to_person_by_username(username, file_path)
                await message.answer(f"✅ Фото добавлено к пользователю {username}.")
            except Exception as e:
                await message.answer(f"❌ Ошибка при добавлении фото: {e}")
            finally:
                await state.clear()
            return

        # --- Распознавание лица (для обычного пользователя) ---
        if state_data == MediaState.waiting_for_photo.state:
            await message.answer("⏳ Распознаю лицо на фото...")
            results = recognize_faces_from_image(file_path)
            for result in results:
                await message.answer(result)
            await state.clear()
            return

        # --- Если состояние не задано ---
        await message.answer("❗ Пожалуйста, сначала нажмите кнопку \"📷 Отправить фото\" или войдите в режим добавления.")
    finally:
        # 🧹 Удаляем файл в любом случае
        if os.path.exists(file_path):
            os.remove(file_path)