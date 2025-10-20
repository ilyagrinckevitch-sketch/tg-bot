import os
import logging
pip install standard-imghdr
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

def start(update: Update, context: CallbackContext):
    update.message.reply_text('✅ Бот работает! Напиши что-нибудь.')

def echo(update: Update, context: CallbackContext):
    update.message.reply_text(f'Ты написал: {update.message.text}')

def main():
    # Используем старый стиль с Updater
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    # Добавляем обработчики
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    
    # Запускаем бота
    logger.info("Бот запущен!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
