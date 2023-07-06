import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import speech_recognition as sr
import KMP_vishing_detector as vd
from decision_tree_classifier import MyDecisionTreeClassifier

# setup telegram bot
updater = Updater(token='6319055640:AAFmM5rltpmE3J-x6fj7LPHxTWt_X0rsVjY', use_context=True)
dt_classifier = MyDecisionTreeClassifier()

QUIZ, END = range(2)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a message or an audio and I will check for vishing.')

# Add this function for /quiz command
def quiz_command(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Starting vishing detection quiz...")
    dt_classifier.start_quiz(update, context)
    return QUIZ

def quiz_response(update: Update, context: CallbackContext) -> int:
    dt_classifier.collect_response(update, context)
    if dt_classifier.is_quiz_complete():
        context.bot.send_message(chat_id=update.effective_chat.id, text="Quiz completed. Analyzing responses...")
        result = dt_classifier.analyze_responses()
        context.bot.send_message(chat_id=update.effective_chat.id, text=result)
        return END
    else:
        return QUIZ

def end(update: Update, context: CallbackContext) -> int:
    return ConversationHandler.END

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

# Add a new CommandHandler for /quiz command
quiz_handler = ConversationHandler(
    entry_points=[CommandHandler('quiz', quiz_command)],
    states={
        QUIZ: [MessageHandler(Filters.text & ~Filters.command, quiz_response)]
    },
    fallbacks=[CommandHandler('cancel', end)],
    conversation_timeout=300,
)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, detect_vishing))
updater.dispatcher.add_handler(MessageHandler(Filters.voice, handle_audio))
updater.dispatcher.add_handler(quiz_handler)

updater.start_polling()
updater.idle()
