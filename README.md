Обнаружение лиц на фото в оболочке тг бота 
Используются cv2 и deepface
Зависимости 
opencv-python (cv2)
numpy
aiogram
python-telegram-bot
Pillow (PIL)
deepface
_________________________________________________________________________________
Установка разом 
```bash
pip install opencv-python numpy aiogram python-telegram-bot pillow deepface
```
По отдельности
```bash
pip install opencv-python
pip install numpy
pip install aiogram
pip install python-telegram-bot
pip install pillow
pip install deepface
```
__________________________________________________________________________________
Основной функционал:
1. /start - запуск бота с кнопкой отправки фото
2. Анализ эмоций на фото с помощью DeepFace
3. Обнаружение лиц с помощью OpenCV
4. Рисование рамок и подписей эмоций на русском
5. Отправка результатов пользователю и админу

Ключевые возможности:
- Распознавание 7 эмоций
- Поддержка русского языка
- Обработка нескольких лиц на фото
