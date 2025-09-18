"""
Бот принимает голосовые сообщения и видео-сообщения (кружочки)
и возвращает их с увеличенной громкостью.
"""

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from utils import normalize_audio_volume, process_video_note

load_dotenv()

# Путь к папке для временных файлов
TMP_DIR = 'tmp'

# Создаем папку tmp, если её нет
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    if voice:
        await process_media(
            update, context,
            file_id=voice.file_id,
            file_type='voice',
            download_ext='ogg',
            send_method=update.message.reply_voice
        )


async def handle_video_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_note = update.message.video_note
    if video_note:
        await process_media(
            update, context,
            file_id=video_note.file_id,
            file_type='video_note',
            download_ext='mp4',
            send_method=update.message.reply_video_note
        )


async def process_media(update: Update, context: ContextTypes.DEFAULT_TYPE, file_id: str, file_type: str, download_ext: str, send_method):
    # Уведомляем пользователя
    await update.message.reply_text(f"Обрабатываю {file_type}...")

    file = await context.bot.get_file(file_id)
    file_name = f"{file_type}_{file_id}.{download_ext}"
    file_path = os.path.join(TMP_DIR, file_name)

    # Скачиваем файл
    await file.download_to_drive(file_path)

    try:
        if file_type == 'voice':
            # Для голосовых используем нормализацию
            output_path = normalize_audio_volume(file_path)
        elif file_type == 'video_note':
            # Для кружочков — обработка видео с усилением звука
            output_path = process_video_note(file_path)
        else:
            raise ValueError("Unsupported file type")

        # Отправляем результат
        with open(output_path, 'rb') as media_file:
            await send_method(
                **{file_type: media_file}
            )

        # Удаляем выходной файл после отправки
        if os.path.exists(output_path):
            os.remove(output_path)

    except Exception as e:
        await update.message.reply_text(f"Ошибка при обработке: {e}")
    finally:
        # Удаляем входной файл
        if os.path.exists(file_path):
            os.remove(file_path)

    print(f"{file_type.capitalize()} обработан: {file_path}")


def main():
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчики
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    app.add_handler(MessageHandler(filters.VIDEO_NOTE, handle_video_note))

    print("Бот запущен...")
    app.run_polling()


if __name__ == '__main__':
    main()