import os
import json
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === Логирование ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))  # опционально, для будущих уведомлений

# === Загрузка FAQ ===
with open('faq.json', 'r', encoding='utf-8') as f:
    FAQ = json.load(f)

# === Кнопки ===
MAIN_KEYBOARD = [
    ["Частые вопросы", "Узнать свою ЗП"],
    ["Связаться с HR"]
]
reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True, one_time_keyboard=False)

# === Обработчики ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я — бот поддержки новых сотрудников.\n\n"
        "Выберите действие ниже или задайте вопрос вручную:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    # Обработка кнопок и текста
    if text == "Узнать свою ЗП" or "зп" in text.lower() or "зарплат" in text.lower():
        # Имитация запроса в БД
        await update.message.reply_text("🔍 Запрашиваю данные из системы оплаты труда...")
        await update.message.reply_text("Ваша зарплата за сентябрь 2025: **87 500 ₽**", parse_mode="Markdown")
        return

    if text == "Связаться с HR":
        await update.message.reply_text("📧 Напишите в HR-отдел: hr@company.com или позвоните по +7 (XXX) XXX-XX-XX.")
        return

    if text == "Частые вопросы":
        questions = "\n".join([f"• {q}" for q in FAQ.keys()])
        await update.message.reply_text(f"Вот список частых вопросов:\n\n{questions}\n\nНапишите вопрос полностью — и я отвечу!")
        return

    # Поиск в FAQ (регистронезависимо)
    for question, answer in FAQ.items():
        if text.lower() in question.lower() or question.lower() in text.lower():
            await update.message.reply_text(answer)
            return

    # Не найдено
    await update.message.reply_text(
        "Извините, я не нашёл ответ на этот вопрос. 😕\n"
        "Попробуйте выбрать из меню или напишите в HR."
    )

# === Уведомления (временно, только для админа) ===
async def notify_salary_sent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 У вас нет прав на эту команду.")
        return
    if len(context.args) != 1:
        await update.message.reply_text("Использование: /notify_salary_sent <user_id>")
        return
    try:
        target_id = int(context.args[0])
        await context.bot.send_message(
            chat_id=target_id,
            text="✅ Ваши реквизиты успешно переданы в банк для перечисления заработной платы."
        )
        await update.message.reply_text("Уведомление отправлено!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

# === Запуск ===
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("notify_salary_sent", notify_salary_sent))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Бот успешно запущен с кнопками и FAQ!")
    application.run_polling()

if __name__ == "__main__":
    main()
