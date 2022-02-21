import configparser
import config
import telebot
import time
from multiprocessing import *
import schedule
import os
from flask import Flask, request


class ScheduleText:

    def __init__(self):
        self.process = Process(target=self.try_send_schedule, args=())

    def sendText(self):
        content_file = open(config.CONTENT_FILE, encoding="utf-8")
        text = content_file.read()

        groups_file = open(config.GROUPS_FILE)
        groups = groups_file.readlines()

        for group in groups:
            bot.send_message(group, text)

    def try_send_schedule(self):
        schedule.every(int(settings['DEFAULT']['minutes'])).minutes.do(self.sendText)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        self.process.start()

    def restart(self):
        schedule.clear()
        self.process.terminate()

        self.process = Process(target=self.try_send_schedule, args=())


bot = telebot.TeleBot(config.TOKEN)
scheduler = ScheduleText()
handlers = {
    'text_change': False,
    'password': False,
}
settings = configparser.ConfigParser()
settings.read(config.SETTINGS_FILE)
APP_URL = f'https://vova-spamer-bot.herokuapp.com/{config.TOKEN}'
server = Flask(__name__)
PORT = int(os.environ.get('PORT', 5000))

def clearHandlers():
    for name, value in handlers.items():
        handlers[name] = False


def findInFile(haystack, needle):
    with open(haystack) as temp_f:
        datafile = temp_f.readlines()
    for line in datafile:
        if str(needle) in line:
            return True
    return False


def isCommand(message):
    return message.startswith('/')


def addAdmin(id):
    admins_file = open(config.ADMINS_FILE, 'a')

    if not findInFile(config.ADMINS_FILE, id):
        admins_file.write(str(id) + "\n")


def touchActiveHandler(message):
    active_handler = list(handlers.keys())[list(handlers.values()).index(True)]

    if active_handler == 'text_change':
        content_file = open(config.CONTENT_FILE, 'w', encoding="utf-8")
        content_file.write(message.text)

        bot.send_message(message.chat.id, config.ANSWERS['text']['completed'])
    elif active_handler == 'password':
        if message.text == config.PASSWORD:
            bot.send_message(message.chat.id, config.ANSWERS['password']['completed'])
            addAdmin(message.chat.id)
        else:
            bot.send_message(message.chat.id, config.ANSWERS['password']['wrong'])
    elif active_handler == 'minutes_change':
        try:
            minutes_count = int(message.text)
        except:
            minutes_count = 0

        if minutes_count > 0:
            settings.set('DEFAULT', 'minutes', message.text)

            with open(config.SETTINGS_FILE, "w") as settings_file:
                settings.write(settings_file)

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


def isAdmin(id):
    return findInFile(config.ADMINS_FILE, id)


@bot.message_handler(commands=['start'])
def start(message):
    groups_file = open(config.GROUPS_FILE, 'a')

    if not findInFile(config.GROUPS_FILE, message.chat.id) and message.chat.type in config.CHAT_TYPES:
        groups_file.write(str(message.chat.id) + "\n")


@bot.message_handler(commands=['send'])
def send(message):
    if message.chat.type == config.PRIVATE_CHAT_TYPE:
        if isAdmin(message.chat.id):
            scheduler.sendText()
        else:
            requestPassword(message)


@bot.message_handler(commands=['text'])
def text(message):
    if message.chat.type == config.PRIVATE_CHAT_TYPE:
        if isAdmin(message.chat.id):
            bot.send_message(message.chat.id, config.ANSWERS['text']['after_command'])
            setActiveHandler('text_change')
        else:
            requestPassword(message)


@bot.message_handler(commands=['cancel'])
def cancel(message):
    if message.chat.type == config.PRIVATE_CHAT_TYPE:
        if isAdmin(message.chat.id):
            bot.send_message(message.chat.id, config.ANSWERS['cancel'])
        else:
            requestPassword(message)


@bot.message_handler(commands=['minutes'])
def minutesChange(message):
    if message.chat.type == config.PRIVATE_CHAT_TYPE:
        if isAdmin(message.chat.id):
            bot.send_message(message.chat.id, config.ANSWERS['minutes']['after_command'])
            setActiveHandler('minutes_change')
        else:
            requestPassword(message)


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
    scheduler.start()

    try:
        # bot.infinity_polling()
        server.run(host='0.0.0.0', port=PORT)
    except:
        pass