import cv2
import numpy as np
from aiogram import Bot
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from deepface import DeepFace

# Токен вашего бота (замените на свой)
TOKEN = "Token_bot"

# Загружаем модель для обнаружения лиц
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Словарь для перевода эмоций с английского на русский
emotion_translation = {
    "angry": "Злой",
    "disgust": "Отвращение",
    "fear": "Страх",
    "happy": "Счастливый",
    "sad": "Грустный",
    "surprise": "Удивление",
    "neutral": "Нейтральный"
}
bot = Bot(token=TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Отправить фото", callback_data="send_photo")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажмите кнопку ниже и отправьте фото для анализа эмоций.",
                                    reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик нажатий на кнопки
    try:
        query = update.callback_query
        await query.answer()
        if query.data == "send_photo":
            await query.message.reply_text("Пожалуйста, отправьте фото человека, и я определю его эмоцию!")
    except Exception as e:
        update.message.reply_text(f"Произошла ошибка {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Обработчик получения фото от пользователя
    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправьте именно фото!")
        return

    # Сообщаем пользователю, что начали обработку
    await update.message.reply_text("🔍 Анализирую фото...")

    try:
        # Загружаем фото
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        # Преобразуем в формат для OpenCV
        img_array = np.frombuffer(photo_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Конвертируем в PIL Image для DeepFace
        pil_image = Image.open(BytesIO(photo_bytes))

        # Анализ эмоций с помощью DeepFace
        try:
            analysis = DeepFace.analyze(np.array(pil_image), actions=["emotion"], enforce_detection=False)
        except Exception as e:
            await update.message.reply_text("😕 Не удалось проанализировать эмоции. Попробуйте другое фото.")
            return

        # Обнаружение лиц на фото
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            await update.message.reply_text("🤷 На фото не обнаружено лиц. Попробуйте другое изображение.")
            return

        # Обрабатываем каждое обнаруженное лицо
        for i, (x, y, w, h) in enumerate(faces):
            # Получаем доминирующую эмоцию
            emotion = analysis[i]['dominant_emotion'] if i < len(analysis) else "unknown"
            translated_emotion = emotion_translation.get(emotion, "Неопределено")

            # Рисуем прямоугольник вокруг лица и подписываем эмоцию
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Используем PIL для поддержки русского текста
            pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)

            try:
                # Пробуем загрузить шрифт (может потребоваться указать полный путь)
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                # Если шрифт не найден, используем стандартный
                font = ImageFont.load_default()

            # Добавляем текст с эмоцией
            draw.text((x, y - 15), translated_emotion, font=font, fill=(0, 0, 0))
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # Подготавливаем результат для отправки
        _, buffer = cv2.imencode('.jpg', img)
        result_bytes = BytesIO(buffer.tobytes())
        result_bytes.seek(0)

        # Отправляем обработанное фото
        await update.message.reply_photo(

            photo=result_bytes,
            caption=f"✅ Готово! Определенные эмоции: {translated_emotion}"
        )
        


    except Exception as e:
        await update.message.reply_text(f"⚠️ Произошла ошибка: {str(e)}")


def main():
    #Основная функция для запуска бота
    print("Запуск бота...")

    # Создаем и настраиваем приложение бота
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Запускаем бота в режиме опроса сервера Telegram
    application.run_polling()
    print("Бот остановлен")


if __name__ == "__main__":
    main()