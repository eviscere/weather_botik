import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
OPENWEATHERMAP_API_KEY = os.environ['OPENWEATHERMAP_API_KEY']

CITY, FREQUENCY = range(2)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Привет! Введите имя города, чтобы узнать температуру.')
    return CITY

def city(update: Update, context: CallbackContext) -> int:
    context.user_data['city'] = update.message.text
    update.message.reply_text('Введите частоту отправки данных (1 - Каждые 10 минут, 2 - Каждые 30 минут, 3 - Каждый час):')
    return FREQUENCY

def frequency(update: Update, context: CallbackContext) -> int:
    context.user_data['frequency'] = update.message.text
    city_name = context.user_data['city']
    temperature = get_temperature(city_name)
    update.message.reply_text(f'Температура в {city_name} составляет {temperature}°C.')
    return ConversationHandler.END

def get_temperature(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['main']['temp']
    else:
        return "Не удалось получить данные о погоде."

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Операция отменена.')
    return ConversationHandler.END

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CITY: [MessageHandler(Filters.text & ~Filters.command, city)],
            FREQUENCY: [MessageHandler(Filters.text & ~Filters.command, frequency)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
