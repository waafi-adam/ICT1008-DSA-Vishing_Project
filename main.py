import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import speech_recognition as sr
import KMP_vishing_detector as vd
from decision_tree_classifier import MyDecisionTreeClassifier

# setup telegram bot
updater = Updater(token='6319055640:AAFmM5rltpmE3J-x6fj7LPHxTWt_X0rsVjY', use_context=True)
dt_classifier = MyDecisionTreeClassifier()

QUIZ, END = range(2)

def start(update: Update, context: CallbackContext) -> None:
    context.user_data['state'] = 'IDLE'  

    keyboard = [[
        InlineKeyboardButton("📝 Start Quiz", callback_data='/quiz') # Inline button for the quiz
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Hello! Send me a message or an audio and I will check for vishing. '
                              'You can also start a vishing detection quiz with the /quiz command or by clicking the button below.', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    # start the quiz if the /quiz button was pressed
    if query.data == '/quiz':
        quiz_command(update, context)

def quiz_command(update: Update, context: CallbackContext) -> int:
    context.user_data['state'] = 'QUIZ'  
    context.bot.send_message(chat_id=update.effective_chat.id, text="Starting vishing detection quiz...")
    dt_classifier.start_quiz(update, context)
    return QUIZ

def quiz_response(update: Update, context: CallbackContext) -> int:
    dt_classifier.collect_response(update, context)
    if dt_classifier.is_quiz_complete():
        context.user_data['state'] = 'IDLE'  
        reply_markup = ReplyKeyboardRemove()  # Remove custom keyboard
        context.bot.send_message(chat_id=update.effective_chat.id, text="Quiz completed. Analyzing responses...", reply_markup=reply_markup)
        result = dt_classifier.analyze_responses()
        context.bot.send_message(chat_id=update.effective_chat.id, text=result, parse_mode='Markdown')
        return END
    else:
        return QUIZ

def end(update: Update, context: CallbackContext) -> int:
    context.user_data['state'] = 'IDLE'
    return ConversationHandler.END

def detect_vishing(update: Update, context: CallbackContext) -> None:
    # Ignore messages if we're in the QUIZ state
    if context.user_data.get('state') == 'QUIZ':
        return

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

    # delete the audio files after processing
    try:
        os.remove('voice.ogg')
        os.remove('voice.wav')
    except Exception as e:
        print("Error deleting audio files: ", e)

quiz_handler = ConversationHandler(
    entry_points=[CommandHandler('quiz', quiz_command)],
    states={
        QUIZ: [MessageHandler(Filters.text & ~Filters.command, quiz_response)]
    },
    fallbacks=[CommandHandler('cancel', end)],
    conversation_timeout=300,
    map_to_parent={
        END: QUIZ, # After ending the conversation, map back to the QUIZ state
    },
)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(quiz_handler)
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, detect_vishing))
updater.dispatcher.add_handler(MessageHandler(Filters.voice, handle_audio))
updater.dispatcher.add_handler(CallbackQueryHandler(button))

updater.start_polling()
updater.idle()
