from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio

# Импортируем все функции из первого файла
from nntu_api import get_today_schedule, get_week_schedule, get_available_groups


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🎓 *Бот расписания ННТУ*\n\n"
        "Доступные команды:\n"
        "/groups - список всех групп\n"
        "/today [группа] - расписание на сегодня\n"
        "/week [группа] - расписание на неделю\n\n"
        "Или просто напишите название группы для расписания на сегодня"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')


async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список групп"""
    await update.message.reply_chat_action('typing')
    groups_text = get_available_groups()
    await update.message.reply_text(groups_text, parse_mode='Markdown')


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на сегодня"""
    if not context.args:
        await update.message.reply_text("Укажите группу: /today АСИ-24-1")
        return

    group_name = ' '.join(context.args)
    await update.message.reply_chat_action('typing')

    schedule_text = get_today_schedule(group_name)
    await update.message.reply_text(schedule_text, parse_mode='Markdown')


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на неделю"""
    if not context.args:
        await update.message.reply_text("Укажите группу: /week АСИ-24-1")
        return

    group_name = ' '.join(context.args)
    await update.message.reply_chat_action('typing')

    schedule_text = get_week_schedule(group_name)
    if len(schedule_text) > 4000:
        parts = [schedule_text[i:i + 4000] for i in range(0, len(schedule_text), 4000)]
        for part in parts:
            await update.message.reply_text(part, parse_mode='Markdown')
            await asyncio.sleep(0.5)
    else:
        await update.message.reply_text(schedule_text, parse_mode='Markdown')


async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает сообщение с названием группы"""
    group_name = update.message.text.strip()
    await update.message.reply_chat_action('typing')

    schedule_text = get_today_schedule(group_name)
    await update.message.reply_text(schedule_text, parse_mode='Markdown')


def main():
    TOKEN = "8139028038:AAHBktcx9y0fuLQeCgISYX_jTnB5br8ngXs"  # Замените на ваш токен

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("groups", groups))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("week", week))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_group_message))

    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()