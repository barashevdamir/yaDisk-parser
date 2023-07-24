from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import requests
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TOKEN = os.getenv("TOKEN")
YANDEX_DISK_TOKEN = os.getenv('YANDEX_DISK_TOKEN')
YANDEX_DISK_API = os.getenv("YANDEX_DISK_API")



def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Open root directory", callback_data='/d/ohiV33J8fP2Fvg')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    path = query.data

    headers = {
        'Authorization': f'OAuth {YANDEX_DISK_TOKEN}',
    }

    params = {
        'path': path,
    }

    response = requests.get(YANDEX_DISK_API, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    if 'file' in data:
        # Получаем ссылку для загрузки файла
        download_url = data['file']
        response = requests.get(download_url, stream=True)

        if response.status_code == 200:
            # Отправляем файл пользователю
            context.bot.send_document(chat_id=update.effective_chat.id, document=download_url, filename=data['name'])
        else:
            query.edit_message_text(text=f"Failed to download the file {data['name']}")
    else:
        keyboard = []
        if '_embedded' in data:
            for item in data['_embedded']['items']:
                keyboard.append([InlineKeyboardButton(item['name'], callback_data=item['path'])])

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=f"Content of the folder {data['name']}:")
        query.message.reply_text('Please choose:', reply_markup=reply_markup)


def main():
    updater = Updater(TOKEN)
    # нужно проверить атрибуты апдейтера и диспатчера

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
