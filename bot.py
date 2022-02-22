import config
import telebot
import time
from multiprocessing import *
import schedule
import logging
import os
import db
from flask import Flask, request

database = db.DB()
database.connect()


class ScheduleText:

    def __init__(self):
        self.process = Process(target=self.try_send_schedule, args=(int(database.getSetting('minutes')),))

    def try_send_schedule(self, minutes):
        schedule.every(15).minutes.do(sendText)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        self.process.start()

    def restart(self):
        schedule.clear()
        self.process.terminate()

        self.process = Process(target=self.try_send_schedule, args=(int(database.getSetting('minutes')),))


logger = telebot.logger
logger.setLevel(logging.DEBUG)
bot = telebot.TeleBot(config.TOKEN)
scheduler = ScheduleText()
handlers = {
    'text_change': False,
    'password': False,
}
APP_URL = f'https://vova-spamer-bot.herokuapp.com/{config.TOKEN}'
server = Flask(__name__)
PORT = int(os.environ.get('PORT', 5000))


def sendText():
    content = open(config.CONTENT_FILE).read()
    groups = database.getGroups()

    for group in groups:
        try:
            bot.send_message(group, content)
        except:
            pass


def clearHandlers():
    for name, value in handlers.items():
        handlers[name] = False


def isCommand(message):
    return message.startswith('/')


def touchActiveHandler(message):
    active_handler = list(handlers.keys())[list(handlers.values()).index(True)]

    if active_handler == 'text_change':
        database.setSetting('content', message.text)
        bot.send_message(message.chat.id, config.ANSWERS['text']['completed'])
    elif active_handler == 'password':
        if message.text == config.PASSWORD:
            bot.send_message(message.chat.id, config.ANSWERS['password']['completed'])
            database.addAdmin(message.chat.id)
        else:
            bot.send_message(message.chat.id, config.ANSWERS['password']['wrong'])
    elif active_handler == 'minutes_change':
        try:
            minutes_count = int(message.text)
        except:
            minutes_count = 0

        if minutes_count > 0:
            database.setSetting('minutes', str(minutes_count))
            # settings.set('DEFAULT', 'minutes', message.text)
            #
            # with open(config.SETTINGS_FILE, "w") as settings_file:
            #     settings.write(settings_file)

            scheduler.restart()

            bot.send_message(message.chat.id, config.ANSWERS['minutes']['completed'])
        else:
            bot.send_message(message.chat.id, config.ANSWERS['minutes']['wrong'])


def setActiveHandler(name):
    clearHandlers()
    handlers[name] = True


def requestPassword(message):
    bot.send_message(message.chat.id, config.ANSWERS['password']['after_command'])
    setActiveHandler('password')


@bot.message_handler(commands=['start'])
def start(message):
    database.addGroup(message.chat.id)


@bot.message_handler(commands=['send'])
def send(message):
    if message.chat.type == config.PRIVATE_CHAT_TYPE:
        if database.isAdmin(message.chat.id):
            bot.send_message(message.chat.id, config.ANSWERS['send']['after_command'])
            sendText()
        else:
            requestPassword(message)


# @bot.message_handler(commands=['text'])
# def text(message):
#     if message.chat.type == config.PRIVATE_CHAT_TYPE:
#         if database.isAdmin(message.chat.id):
#             bot.send_message(message.chat.id, config.ANSWERS['text']['after_command'])
#             setActiveHandler('text_change')
#         else:
#             requestPassword(message)


# @bot.message_handler(commands=['cancel'])
# def cancel(message):
#     if message.chat.type == config.PRIVATE_CHAT_TYPE:
#         if database.isAdmin(message.chat.id):
#             bot.send_message(message.chat.id, config.ANSWERS['cancel'])
#         else:
#             requestPassword(message)


# @bot.message_handler(commands=['minutes'])
# def minutesChange(message):
#     if message.chat.type == config.PRIVATE_CHAT_TYPE:
#         if database.isAdmin(message.chat.id):
#             bot.send_message(message.chat.id, config.ANSWERS['minutes']['after_command'])
#             setActiveHandler('minutes_change')
#         else:
#             requestPassword(message)

@bot.message_handler(content_types=['text'])
def handle_messages(message):
    if not isCommand(message.text):
        touchActiveHandler(message)
        clearHandlers()


@server.route('/' + config.TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200


if __name__ == '__main__':
    try:
        # scheduler.start()

        bot.remove_webhook()
        bot.set_webhook(APP_URL)

        server.run(host='0.0.0.0', port=PORT)
    except Exception as _ex:
        print("[INFO] Error: ", _ex)
