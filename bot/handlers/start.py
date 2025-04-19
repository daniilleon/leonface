from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from bot.config import ADMIN_IDS
from bot.fsm.states import MediaState

router = Router()

# Главное меню для обычного пользователя
user_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📷 Отправить фото"),
            KeyboardButton(text="🎥 Отправить видео")
        ]
    ],
    resize_keyboard=True
)

# Главное меню для админа (с кнопкой "Админка")
admin_main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📷 Отправить фото"),
            KeyboardButton(text="🎥 Отправить видео")
        ],
        [KeyboardButton(text="🛠 Админка")]
    ],
    resize_keyboard=True
)

# Меню внутри админки
admin_panel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить профиль"),
            KeyboardButton(text="Добавить фото к профилю")
        ],
        [
            KeyboardButton(text="Редактировать профиль"),
            KeyboardButton(text="Назад")
        ],
    ],
    resize_keyboard=True
)


@router.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    if user_id in ADMIN_IDS:
        await message.answer(
            "🔐 Привет, Админ!",
            reply_markup=admin_main_kb
        )
    else:
        await message.answer(
            "Привет, я бот для распознавания лиц\n\n📸 Пришли мне фото\n📽 Или видео — я распознаю, кто на нём.",
            reply_markup=user_menu_kb
        )


# Пользователь выбрал обычное фото
@router.message(F.text == "📷 Отправить фото")
async def set_waiting_for_photo(message: Message, state: FSMContext):
    await state.set_state(MediaState.waiting_for_photo)
    await message.answer("📷 Жду фото для распознавания...")


# Пользователь выбрал видео
@router.message(F.text == "🎥 Отправить видео")
async def set_waiting_for_video(message: Message, state: FSMContext):
    await state.set_state(MediaState.waiting_for_video)
    await message.answer("🎥 Жду видео для распознавания...")


# Админ нажал на кнопку "Админка"
@router.message(F.text == "🛠 Админка")
async def show_admin_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🛠 Админ-меню:", reply_markup=admin_panel_kb)


# Назад в главное меню (из админки)
@router.message(F.text == "Назад")
async def go_back_to_main(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        await message.answer("Главное меню:", reply_markup=admin_main_kb)
    else:
        await message.answer("Главное меню:", reply_markup=user_menu_kb)
