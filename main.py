from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Define the start command handler
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('This is Abu Bakr Siddique')

def main():
    # Replace 'YOUR_TOKEN' with your actual bot token
    application = Application.builder().token("7319521554:AAFuRROy2ZJbmy1K1vYRNQIfxwX5P1ReDi4").build()

    # Register the start command handler
    print("This a telegram bot")
    application.add_handler(CommandHandler("start", start))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()