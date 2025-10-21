import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === Настройка логирования ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')

# === База FAQ (для MVP — в коде, позже вынесёшь в JSON/БД) ===
FAQ = {
    "как устроиться": "Чтобы устроиться, пришлите резюме на hr@company.com",
    "документы нужны": "Паспорт, СНИЛС, ИНН, диплом",
    "сколько зп": "Зарплата зависит от должности. Напишите 'моя зп', чтобы узнать вашу.",
    "график работы": "График: 5/2, с 9:00 до 18:00",
    # ... остальные 46 вопросов
}

# === Функции ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот поддержки новых сотрудников.\n"
        "Задайте вопрос — например: «Как устроиться?», «Какие документы нужны?»"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    user_id = update.effective_user.id

    # Проверка на динамический запрос: "моя зп"
    if "моя зп" in text or "моя зарплата" in text:
        salary = get_salary(user_id)
        await update.message.reply_text(salary)
        return

    # Поиск в FAQ
    for question, answer in FAQ.items():
        if question in text:
            await update.message.reply_text(answer)
            return

    # Если ничего не найдено
    await update.message.reply_text(
        "Извините, я не нашёл ответ на ваш вопрос. "
        "Попробуйте задать его иначе или напишите в HR."
    )

def get_salary(user_id: int) -> str:
    # Заглушка: в реальности тут запрос к БД
    # Например: SELECT salary FROM payroll WHERE telegram_id = user_id
    return "Ваша зарплата за сентябрь 2025: 87 500 ₽"

# === Уведомления от бухгалтерии (MVP-версия) ===
async def notify_salary_sent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Только для админа (можно добавить проверку по user_id)
    if len(context.args) != 1:
        await update.message.reply_text("Использование: /notify_salary_sent <user_id>")
        return
    try:
        target_user_id = int(context.args[0])
        await context.bot.send_message(
            chat_id=target_user_id,
            text="✅ Ваши банковские реквизиты успешно переданы в банк для перечисления заработной платы."
        )
        await update.message.reply_text("Уведомление отправлено!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("notify_salary_sent", notify_salary_sent))  # только для демо
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Бот успешно запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
