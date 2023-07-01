import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import speech_recognition as sr
import KMP_vishing_detector as vd

# setup telegram bot
updater = Updater(token='6319055640:AAFmM5rltpmE3J-x6fj7LPHxTWt_X0rsVjY', use_context=True)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a message or an audio and I will check for vishing.')

def detect_vishing(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text.lower()
    result, percentage, vishing_type = vd.detect_vishing(user_text)
    if result == "Vishing":
        update.message.reply_text(f'*Vishing Detected!* 🚨\nThe message has a *{percentage:.2f}%* likelihood of being a vishing attempt.\n\n*Type of Vishing:* {vishing_type}', parse_mode='Markdown')
    else:
        update.message.reply_text(f'Good news! 🎉\nThe message seems safe with a low vishing likelihood of *{percentage:.2f}%*. Always stay alert!', parse_mode='Markdown')

def handle_audio(update: Update, context: CallbackContext) -> None:
    file = context.bot.get_file(update.message.voice.file_id)
    file.download('voice.ogg')

    # assuming that you have ffmpeg installed
    # convert the audio file to wav
    os.system("ffmpeg -y -i voice.ogg voice.wav")


    r = sr.Recognizer()
    with sr.AudioFile('voice.wav') as source:
        audio = r.record(source)
        user_text = r.recognize_google(audio, language='en-US')
        result, percentage, vishing_type = vd.detect_vishing(user_text)
        if result == "Vishing":
            update.message.reply_text(f'*Vishing Detected in Audio!* 🚨\nThe audio has a *{percentage:.2f}%* likelihood of being a vishing attempt.\n\n*Type of Vishing:* {vishing_type}', parse_mode='Markdown')
        else:
            update.message.reply_text(f'Good news! 🎉\nThe audio seems safe with a low vishing likelihood of *{percentage:.2f}%*. Always stay alert!', parse_mode='Markdown')

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, detect_vishing))
updater.dispatcher.add_handler(MessageHandler(Filters.voice, handle_audio))

updater.start_polling()
updater.idle()
