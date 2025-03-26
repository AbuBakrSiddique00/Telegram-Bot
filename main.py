from telegram import InlineKeyboardButton,InlineKeyboardMarkup, Update
from telegram.ext import  Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
import os 
import logging
from dotenv import load_dotenv
from google import genai

#Load the .env file first 
load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

is_registered = False

# Define the start command handler
async def start(update: Update, context: CallbackContext):
    global is_registered 
    is_registered = False
    
    print("---------------------------")
    print("...Started...")
    print("---------------------------")

    await update.message.reply_text("It's fun time Dude.\n"
    "I am a     fine tuned LLM model. \n"
    "First you have to register your account by typing /register. \n"
    "Then, Ask whatever you want and get fun!")
async def register(update: Update, context: CallbackContext):
    "Send inline buttons for PIN entry."

    context.user_data["pin_code"] = ""
    print("---------------------------")
    print("Registration Requested")
    print("---------------------------")

    await update.message.reply_text(
        "We have you a 5 digit code",
        reply_markup=generate_keypad(),
    )

def generate_keypad():
    """Generate initial keypad"""
    keyboard = [
         [
            InlineKeyboardButton("1", callback_data="1"),
            InlineKeyboardButton("2", callback_data="2"),
            InlineKeyboardButton("3", callback_data="3"),
        ],
        [
            InlineKeyboardButton("4", callback_data="4"),
            InlineKeyboardButton("5", callback_data="5"),
            InlineKeyboardButton("6", callback_data="6"),
        ],
        [
            InlineKeyboardButton("7", callback_data="7"),
            InlineKeyboardButton("8", callback_data="8"),
            InlineKeyboardButton("9", callback_data="9"),
        ],
        [
            InlineKeyboardButton("0", callback_data="0"),
            InlineKeyboardButton("⌫", callback_data="delete"),
        ],
        [InlineKeyboardButton("✅ Enter", callback_data="enter")],
    ]
    return InlineKeyboardMarkup(keyboard)
    
async def handle_button_click(update: Update, context: CallbackContext):
    """Handle initial button clicks (number, delete, enter)"""
    query = update.callback_query
    await query.answer()

    user_input = query.data
    pin_code = context.user_data.get("pin_code", "")

    if user_input.isdigit():
        if len(pin_code) < 5:
            pin_code += user_input
            context.user_data["pin_code"] = pin_code
        else:
            await query.message.reply_text("❌ You have already entered 5 digits.")
    elif user_input == "delete":
        pin_code = pin_code[:-1]
        context.user_data["pin_code"] = pin_code
    elif user_input == "enter":
        if len(pin_code) == 5:
            await query.message.edit_text(f"Sending PIN: {pin_code} to the server...")
            # Here send `pin_code` to your backend verification
           
            print("---------------------------")
            print(pin_code)
            print("---------------------------")
            x =  int(input())
            if x != 0:
                global is_registered
                is_registered = True
            else:
                print("here")
                is_registered = False
            if is_registered:
                await query.message.reply_text("PIN verified! you can chat now with me.")
            else:
                await query.message.reply_text("❌ Wrong PIN, Please Enter the correct PIN")
        else:
            await query.message.reply_text(
                "❌ Invalid PIN: Please enter exactly 5 digits. "
            )

            # Reset 
        context.user_data["pin_code"] = ""
        return
        
    await query.message.reply_text(f"Current PIN: {context.user_data['pin_code']}", reply_markup = generate_keypad())

async def chat(update: Update, coontext: CallbackContext):
    """Handle  user Prompt and response with Open AI GPT-4o"""
    user_message = update.message.text
    print("----------Chat----------")
    print(user_message, is_registered)

    if not is_registered:
        await update.message.reply_text("Please Register your Account first by Typing /register")
        return
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{
                "parts": [{
                    "text": """You are a funny chat bot. Reply to messages only in Banglish.
                            Make funny and super romantic jokes that will make users laugh.
                            Be creative and ask engaging questions.
                            Keep responses short and sweet."""
                }, {
                    "text": user_message
                }]
            }],
        )
        reply = response.text
        print("------------------------")
        print("Reply: \n\n", reply)
        print("------------------------")
        await update.message.reply_text(reply)

    except Exception as e:
        reply = "Sorry, Something went wrong. Please try again later"
        logging.error(f"Error: {e}")
        await update.message.reply_text(reply)

def main():
    # Run the bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler( CallbackQueryHandler(handle_button_click))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )


    # Start the Bot
    application.run_polling()

    logging.info("Bot started...")
    application.run_polling()

if __name__ == '__main__':
    main()