"""
Бот принимает голосовые сообщения и 
"""

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from utils import normalize_audio_volume

load_dotenv()

# Путь к папке для временных файлов
TMP_DIR = 'tmp'

# Создаем папку tmp, если её нет
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем объект голосового сообщения
    voice = update.message.voice

    if not voice:
        return

    # Уведомляем пользователя, что файл обрабатывается
    processing_message = await update.message.reply_text("Обрабатываю голосовое сообщение...")

    # Получаем файл через Telegram API
    file = await context.bot.get_file(voice.file_id)
    file_name = f"voice_{voice.file_id}.ogg"
    file_path = os.path.join(TMP_DIR, file_name)

    # Скачиваем файл локально
    await file.download_to_drive(file_path)

    try:
        # Обрабатываем файл
        normalized_file_path = normalize_audio_volume(file_path)

        # Удаляем сообщение "обрабатывается..."
        await context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=processing_message.message_id
        )

        # Отправляем файл
        with open(normalized_file_path, 'rb') as audio_file:
            await update.message.reply_voice(
                voice=audio_file,
                caption="Вот ваше голосовое (от меня!)"
            )

        # Удаляем промежуточный файл
        if os.path.exists(normalized_file_path):
            os.remove(normalized_file_path)
    except RuntimeError as e:
        await update.message.reply_text(f'Не удалось обработать голосовое сообщение, ошибка: {e}')
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    # Подтверждение сохранения
    print(f"Голосовое сообщение сохранено: {file_path}")


def main():
    TOKEN = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(TOKEN).build()

    voice_handler = MessageHandler(filters.VOICE, handle_voice_message)
    app.add_handler(voice_handler)

    app.run_polling()


if __name__ == '__main__':
    main()