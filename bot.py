import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, Filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('✅ Бот работает! Напиши что-нибудь.')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Ты написал: {update.message.text}')

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(Filters.TEXT & ~filters.COMMAND, echo))

    logger.info("🤖 Бот успешно запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
