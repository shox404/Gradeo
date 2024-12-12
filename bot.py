# import logging 
# from aiogram import Bot, Dispatcher, executor, types 
# from googletrans import Translator 
# from langdetect import detect 
 
# API_TOKEN = '7523832529:AAFtuyaPS9Dt2YWSvQXb1b6_MeUDT0naGKQ' 
 
# logging.basicConfig(level=logging.INFO) 
 
# bot = Bot(token=API_TOKEN) 
# dp = Dispatcher(bot) 
# translator = Translator() 
 
# LANGUAGES = { 
#     'en': 'English', 
#     'ru': 'Русский', 
#     'uzb': 'Uzbek' 
# } 
 
# @dp.message_handler() 
# async def handle_message(message: types.Message): 
#     try: 
#         user_lang = detect(message.text) 
#         user_lang = user_lang if user_lang in LANGUAGES else 'en' 
 
#         translated_text = translator.translate(message.text, src=user_lang, dest='en').text 
 
#         reply_text = translator.translate(f"Your message is: {translated_text}", src='en', dest=user_lang).text 
#         await message.reply(reply_text) 
#     except Exception as e: 
#         logging.error(f"Error: {e}") 
#         await message.reply("An error occurred while processing your message.") 
 
# if __name__ == '__main__': 
#     executor.start_polling(dp, skip_updates=True)
from telegram import Update 
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    await update.message.reply_text('Привет! Я ваш Telegram-бот. Чем могу помочь?') 
 
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    await update.message.reply_text('Доступные команды:\n/start - начать\n/help - помощь') 
 
async def main(): 
 
    TOKEN = '8188247842:AAEU5JIcSZIIHPOLvSyzPdKsIYxJ7JTC0CU' 
 
    application = ApplicationBuilder().token(TOKEN).build() 
 
    application.add_handler(CommandHandler("start", start)) 
    application.add_handler(CommandHandler("help", help_command)) 
 
    print("Бот запущен...") 
    await application.run_polling() 
 
if name == "__main__": 
    import asyncio 
    asyncio.run(main())