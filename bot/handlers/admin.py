import os
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from bot.fsm.states import AddUserStates, AddPhotoStates, EditProfileStates
from bot.config import DOWNLOAD_DIR
from core.add_person import add_person_by_data
from core.add_photo_to_person import add_photo_to_person_by_username
from core.db import update_person, get_person_by_username_full, update_single_field

router = Router()

# ➕ Добавление нового пользователя
@router.message(F.text == "Добавить профиль")
async def start_add_user(message: Message, state: FSMContext):
    await state.set_state(AddUserStates.waiting_for_photo)
    await message.answer("📷 Отправьте фото пользователя")


@router.message(AddUserStates.waiting_for_photo, F.photo)
async def receive_user_photo(message: Message, state: FSMContext):
    file = message.photo[-1]
    file_path = os.path.join(DOWNLOAD_DIR, f"user_{message.from_user.id}.jpg")
    await file.download_to_destination(file_path)
    await state.update_data(photo_path=file_path)
    await state.set_state(AddUserStates.waiting_for_first_name)
    await message.answer("📝 Введите имя:")


@router.message(AddUserStates.waiting_for_first_name)
async def get_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(AddUserStates.waiting_for_last_name)
    await message.answer("📝 Введите фамилию:")


@router.message(AddUserStates.waiting_for_last_name)
async def get_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(AddUserStates.waiting_for_username)
    await message.answer("👤 Введите логин (username):")


@router.message(AddUserStates.waiting_for_username)
async def get_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await state.set_state(AddUserStates.waiting_for_phone)
    await message.answer("📞 Введите телефон:")


@router.message(AddUserStates.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(AddUserStates.waiting_for_telegram)
    await message.answer("💬 Введите Telegram (без @):")


@router.message(AddUserStates.waiting_for_telegram)
async def get_telegram(message: Message, state: FSMContext):
    await state.update_data(telegram=message.text)
    await state.set_state(AddUserStates.waiting_for_whatsapp)
    await message.answer("💚 Введите WhatsApp (только номер):")


@router.message(AddUserStates.waiting_for_whatsapp)
async def finish_add_user(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_path = data.get("photo_path")

    try:
        result = add_person_by_data(
            image_path=photo_path,
            first_name=data["first_name"],
            last_name=data["last_name"],
            username=data["username"],
            phone=data["phone"],
            telegram=data["telegram"],
            whatsapp=message.text
        )
        await message.answer(result)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении: {e}")

    await state.clear()


# ➕ Добавление фото к существующему пользователю
@router.message(F.text == "Добавить фото к профилю")
async def start_add_photo(message: Message, state: FSMContext):
    await state.set_state(AddPhotoStates.waiting_for_username)
    await message.answer("👤 Введите логин пользователя, к которому хотите добавить фото:")


@router.message(AddPhotoStates.waiting_for_username)
async def get_username_to_add_photo(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await state.set_state(AddPhotoStates.waiting_for_photo)
    await message.answer("📷 Отправьте фото:")


@router.message(AddPhotoStates.waiting_for_photo, F.photo)
async def add_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    file = message.photo[-1]
    file_path = os.path.join(DOWNLOAD_DIR, f"extra_{message.from_user.id}.jpg")
    await file.download_to_destination(file_path)

    try:
        add_photo_to_person_by_username(data["username"], file_path)
        await message.answer("✅ Фото успешно добавлено!")
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении фото: {e}")

    await state.clear()


# ✏️ Редактировать профиль
@router.message(F.text == "Редактировать профиль")
async def start_edit_profile(message: Message, state: FSMContext):
    await state.set_state(EditProfileStates.waiting_for_username)
    await message.answer("👤 Введите логин пользователя, которого хотите отредактировать:")


edit_field_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Имя"), KeyboardButton(text="Фамилия")],
        [KeyboardButton(text="Телефон"), KeyboardButton(text="Telegram")],
        [KeyboardButton(text="WhatsApp"), KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

@router.message(EditProfileStates.waiting_for_username)
async def choose_field_to_edit(message: Message, state: FSMContext):
    username = message.text
    person = get_person_by_username_full(username)
    if not person:
        await message.answer("❌ Пользователь не найден.")
        await state.clear()
        return

    await state.update_data(username=username)
    await message.answer(
        f"👤 Текущие данные:\n"
        f"Имя: {person[1]}\n"
        f"Фамилия: {person[2]}\n"
        f"Телефон: {person[4]}\n"
        f"Telegram: {person[5]}\n"
        f"WhatsApp: {person[6]}\n\n"
        f"Выберите поле для изменения:",
        reply_markup=edit_field_kb
    )
    await state.set_state(EditProfileStates.choosing_field)


@router.message(EditProfileStates.choosing_field)
async def select_field(message: Message, state: FSMContext):
    fields = {
        "Имя": "first_name",
        "Фамилия": "last_name",
        "Телефон": "phone",
        "Telegram": "telegram",
        "WhatsApp": "whatsapp"
    }
    field = fields.get(message.text.strip())
    if not field:
        await message.answer("❌ Неверное поле. Попробуйте снова.")
        return
    await state.update_data(field_to_edit=field)
    await state.set_state(EditProfileStates.waiting_for_new_value)
    await message.answer("✏️ Введите новое значение:")


@router.message(EditProfileStates.waiting_for_new_value)
async def save_new_value(message: Message, state: FSMContext):
    data = await state.get_data()
    username = data["username"]
    field = data["field_to_edit"]
    value = message.text.strip()

    try:
        update_single_field(username=username, field=field, value=value)
        await message.answer("✅ Данные успешно обновлены!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении: {e}")

    await state.clear()