from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from bot.fsm.states import MediaState
from core.recognize_video import recognize_faces_on_video
from bot.loader import bot
from bot.config import DOWNLOAD_DIR
import os
import uuid

router = Router()

@router.message(F.content_type.in_([types.ContentType.VIDEO, types.ContentType.VIDEO_NOTE]))
async def handle_video(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state != MediaState.waiting_for_video.state:
        await message.reply("Пожалуйста, сначала нажмите кнопку 🎥 Отправить видео")
        return

    await state.clear()
    await message.reply("🎥 Обрабатываю видео...")

    video = message.video or message.video_note
    file_info = await bot.get_file(video.file_id)
    file_path = file_info.file_path

    local_path = os.path.join(DOWNLOAD_DIR, f"{uuid.uuid4()}.mp4")
    await bot.download_file(file_path, local_path)

    results = recognize_faces_on_video(local_path)
    os.remove(local_path)

    if results:
        for result in results:
            await message.reply(result)
    else:
        await message.reply("❌ Лица не найдены.")
