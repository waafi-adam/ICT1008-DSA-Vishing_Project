import os
import importlib
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import speech_recognition as sr
from detection_modules.quiz_decision_tree import MyDecisionTreeClassifier

# setup telegram bot
updater = Updater(token='6319055640:AAFmM5rltpmE3J-x6fj7LPHxTWt_X0rsVjY', use_context=True)
dt_classifier = MyDecisionTreeClassifier()

# Default vishing detection module
vishing_detector = importlib.import_module('detection_modules.trie_vishing_detection')

QUIZ, END = range(2)

def set_module(update: Update, context: CallbackContext) -> None:
    if context.args:
        module_name = ' '.join(context.args)
        if module_name not in ['cosineSim', 'gensim', 'kmp', 'nltk', 'sklearn', 'spacy', 'trie']:
            update.message.reply_text(f'Oops! 🙅‍♂️ Invalid module name: {module_name}\nTry one from these: cosineSim, gensim, kmp, nltk, sklearn, spacy, trie.')
        else:
            update.message.reply_text(f'Hang on... 🔄 Loading module: {module_name}...')
            global vishing_detector
            vishing_detector = importlib.import_module(f'detection_modules.{module_name}_vishing_detection')
            update.message.reply_text(f'All set! ✅ Detection module changed to: {module_name}')
    else:
        update.message.reply_text(f'Current detection module is: {vishing_detector.__name__}\nTo switch it up, use the command: /set_module <module_name>')

def start(update: Update, context: CallbackContext) -> None:
    context.user_data['state'] = 'IDLE'  

    update.message.reply_text(
        f'👋 Hello there! Ready to test messages or audios for vishing? Just send them over! \n\n'
        'Feeling like a detective? 🔍 Start a vishing detection quiz with /quiz. \n\n'
        f'🔧 We are currently using the {vishing_detector.__name__} detection module. '
        'Want to try another module? Use /set_module <module_name>. Available modules are: cosineSim, gensim, kmp, nltk, sklearn, spacy, trie.'
    )


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

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
        reply_markup = ReplyKeyboardRemove()  
        context.bot.send_message(chat_id=update.effective_chat.id, text="Quiz completed. Analyzing responses...", reply_markup=reply_markup)
        result_1 = dt_classifier.analyze_responses()
        context.bot.send_message(chat_id=update.effective_chat.id, text=result_1, parse_mode='Markdown')
        return END
    else:
        return QUIZ

def end(update: Update, context: CallbackContext) -> int:
    context.user_data['state'] = 'IDLE'
    return ConversationHandler.END

def format_reply(module_name, result_1, result_2, result_3):
    if module_name in ['detection_modules.kmp_vishing_detection', 'detection_modules.trie_vishing_detection']:
        if result_1 == "Vishing":
            return f'*Vishing Detected!* 🚨\nThe message has a *{result_2:.2f}* likelihood of being a vishing attempt.\n\n*Type of Vishing:* {result_3}'
        else:
            return f'Good news! 🎉\nThe message seems safe with a low vishing likelihood of *{result_2:.2f}*. Always stay alert!'
    else:
        if result_2 > result_3:
            return f'*Vishing Detected!* 🚨\nThe message similarity to a vishing attempt is *{result_2:.2f}* and to a non-vishing content is *{result_3:.2f}*. Always stay alert!'
        else:
            return f'Good news! 🎉\nThe message seems safe. Its similarity to a vishing attempt is *{result_2:.2f}* and to a non-vishing content is *{result_3:.2f}*. Always stay alert!'

def detect_vishing(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('state') == 'QUIZ':
        return

    user_text = update.message.text.lower()
    result_1, result_2, result_3 = vishing_detector.detect_vishing(user_text)
    reply_message = format_reply(vishing_detector.__name__, result_1, result_2, result_3)
    update.message.reply_text(reply_message, parse_mode='Markdown')

def handle_audio(update: Update, context: CallbackContext) -> None:
    file = context.bot.get_file(update.message.voice.file_id)
    file.download('voice.ogg')
    os.system("ffmpeg -y -i voice.ogg voice.wav")
    r = sr.Recognizer()
    with sr.AudioFile('voice.wav') as source:
        audio = r.record(source)
        user_text = r.recognize_google(audio, language='en-US')
        result_1, result_2, result_3 = vishing_detector.detect_vishing(user_text)
        reply_message = format_reply(vishing_detector.__name__, result_1, result_2, result_3)
        update.message.reply_text(reply_message, parse_mode='Markdown')

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
        END: QUIZ,
    },
)


updater.dispatcher.add_handler(CommandHandler('set_module', set_module))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(quiz_handler)
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, detect_vishing))
updater.dispatcher.add_handler(MessageHandler(Filters.voice, handle_audio))

updater.start_polling()
updater.idle()