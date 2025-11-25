from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

async def scheduled_broadcast(context: ContextTypes.DEFAULT_TYPE):
    """Broadcast otomatis setiap jam"""
    for group_id in TARGET_GROUPS:
        try:
            await context.bot.send_message(
                chat_id=group_id,
                text=BROADCAST_MESSAGE,
                parse_mode='Markdown'
            )
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error: {e}")

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    
    # Setup scheduler (broadcast setiap 2 jam)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_broadcast, "interval", hours=2, args=[application.context_types.DEFAULT_TYPE()])
    scheduler.start()
    
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
