import os
import json
import asyncio
import logging
import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === Настройка ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

# === Вспомогательная функция: очистка текста для сравнения ===
def normalize(text: str) -> str:
    """Удаляет знаки препинания и приводит к нижнему регистру."""
    return re.sub(r'[^\w\s]', '', text).strip().lower()

# === Загрузка FAQ ===
with open('faq.json', 'r', encoding='utf-8') as f:
    FAQ = json.load(f)

# Нормализованные ключи для быстрого поиска
FAQ_NORMALIZED = {normalize(q): a for q, a in FAQ.items()}

# === Клавиатура ===
MAIN_KEYBOARD = [
    ["Частые вопросы", "Узнать свою ЗП"],
    ["Связаться с HR"]
]
reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

# === Функция "зарплата" ===
def get_salary_info(user_id: int) -> str:
    salaries = {
        123456789: "92 300 ₽",
        987654321: "78 500 ₽",
    }
    salary = salaries.get(user_id, "85 000 ₽")
    return f"Ваша начисленная зарплата за сентябрь 2025: **{salary}**"

# === Обработчики ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я — бот поддержки новых сотрудников.\n\n"
        "Выберите действие или задайте вопрос:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id
    if not text:
        return

    normalized_input = normalize(text)

    # --- 1. Точное совпадение с FAQ (нормализованное) ---
    if normalized_input in FAQ_NORMALIZED:
        await update.message.reply_text(FAQ_NORMALIZED[normalized_input])
        return

    # --- 2. Обработка кнопок и ключевых слов ---
    text_lower = text.lower()

    # Зарплата: срабатывает ТОЛЬКО если это не вопрос из FAQ
    if text == "Узнать свою ЗП" or any(kw in text_lower for kw in ["зп", "зарплат", "оклад", "деньги"]):
        await update.message.reply_text("🔍 Запрашиваю данные из системы расчёта заработной платы...")
        await asyncio.sleep(1.2)
        salary_msg = get_salary_info(user_id)
        await update.message.reply_text(salary_msg, parse_mode="Markdown")
        return

    if text == "Связаться с HR":
        await update.message.reply_text(
            "📧 Напишите в HR-отдел:\n"
            "— Email: hr@company.com\n"
            "— Телефон: +7 (495) 123-45-67"
        )
        return

    if text == "Частые вопросы":
        questions = "\n".join([f"• {q}" for q in FAQ.keys()])
        await update.message.reply_text(
            f"Часто задаваемые вопросы:\n\n{questions}\n\nНапишите вопрос — и я отвечу!"
        )
        return

    # --- 3. Не найдено ---
    await update.message.reply_text(
        "Извините, я не нашёл ответ на этот вопрос. 😕\n"
        "Попробуйте выбрать из меню или напишите в HR."
    )

# === Уведомления (только для админа) ===
async def notify_salary_sent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADMIN_ID or update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Эта команда доступна только администратору.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Использование: /notify_salary_sent <user_id>")
        return

    try:
        target_id = int(context.args[0])
        await context.bot.send_message(
            chat_id=target_id,
            text="✅ Ваши банковские реквизиты успешно переданы в банк для перечисления заработной платы."
        )
        await update.message.reply_text(f"Уведомление отправлено пользователю {target_id}!")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

# === Запуск ===
def main():
    if not BOT_TOKEN:
        raise ValueError("Переменная BOT_TOKEN не задана!")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("notify_salary_sent", notify_salary_sent))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Бот запущен! Админ ID: %s", ADMIN_ID if ADMIN_ID else "не задан")
    application.run_polling()

if __name__ == "__main__":
    main()
