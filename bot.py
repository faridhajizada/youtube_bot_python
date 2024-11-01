# TOKEN = "7089049710:AAE1Fm2rJeOLFHS1W1rvjPhcQZpG3on6KV4"
import os
import yt_dlp
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Разрешаем вложенные циклы событий
nest_asyncio.apply()

# Замените 'YOUR_TELEGRAM_BOT_TOKEN' на ваш токен
TOKEN = "7089049710:AAE1Fm2rJeOLFHS1W1rvjPhcQZpG3on6KV4"

def format_file_size(size):
    """Функция для форматирования размера файла в человекочитаемый вид (KB или MB)."""
    if size < 1024:
        return f"{size} Б"
    elif size < 1048576:  # 1024 * 1024
        return f"{size / 1024:.2f} КБ"
    else:
        return f"{size / 1048576:.2f} МБ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Пожалуйста, отправьте ссылку на видео с YouTube.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    if 'youtube.com' in url or 'youtu.be' in url:
        await update.message.reply_text("Получение информации о видео...")

        # Параметры для получения информации о видео
        ydl_opts_info = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            try:
                # Получаем информацию о видео
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict['title']
                duration = info_dict['duration']
                publish_date = info_dict['upload_date']
                filesize = info_dict.get('filesize', 'N/A')
                channel_icon_url = info_dict.get('uploader_url', '') + '/favicon.ico'  # URL иконки канала

                # Форматируем размер файла
                formatted_filesize = format_file_size(filesize) if isinstance(filesize, int) else 'N/A'

                # Информируем пользователя о видео
                await update.message.reply_text(
                    f"**Название:** {title}\n"
                    f"**Длина видео:** {duration // 60} мин {duration % 60} сек\n"
                    # f"**Дата публикации:** {publish_date}\n"
                    f"**Размер файла:** {formatted_filesize}\n"
                    "Начинаю загрузку аудио в формате MP3..."
                )

                # Параметры для скачивания MP3
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': './downloads/%(title)s.%(ext)s',
                    'noplaylist': True,
                    'quiet': True
                }

                # Создаем директорию для загрузок, если не существует
                if not os.path.exists('./downloads'):
                    os.makedirs('./downloads')

                # Скачивание аудио
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    await update.message.reply_text("Аудио загружено! Отправляю файл...")
                    # Получаем имя файла
                    file_name = f"./downloads/{title}.mp3"

                    # Сначала отправляем изображение канала
                    await context.bot.send_photo(
                        chat_id=update.message.chat.id,
                        photo=channel_icon_url,
                        caption=f"Иконка канала: {info_dict['uploader']}"
                    )

                    # Затем отправляем аудио
                    await context.bot.send_audio(
                        chat_id=update.message.chat.id,
                        audio=open(file_name, 'rb'),
                        # caption=title
                    )
            except Exception as e:
                await update.message.reply_text(f"Произошла ошибка: {str(e)}")
    else:
        await update.message.reply_text("Ссылка на видео невалидна. Пожалуйста, попробуйте еще раз.")

async def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())