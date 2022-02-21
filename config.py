TOKEN = '5263152543:AAGhJJT8L3SjKEhjcqq0ecbXNh4KROoL_7g'
CONTENT_FILE = 'content.txt'
GROUPS_FILE = 'groups.txt'
ADMINS_FILE = 'admins.txt'
SETTINGS_FILE = "settings.ini"
CHAT_TYPES = ['group', 'supergroup']
PRIVATE_CHAT_TYPE = 'private'
ANSWERS = {
    'cancel': "Операция отменена",
    'text': {
        'after_command': 'Введите новый текст:',
        'completed': 'Текст успешно изменен',
    },
    'password': {
        'after_command': 'Введите пароль:',
        'completed': 'Вы успешно вошли как админ',
        'wrong': 'Неверный пароль',
    },
    'minutes': {
        'after_command': 'Введите кол-во минут:',
        'completed': 'Настройки успешно обновлены',
        'wrong': 'Вы ввели некорректное число',
    }
}
COMMANDS = {
    'cancel': 'cancel',
    'start': 'start',
    'text': 'text',
}
PASSWORD = 'qwertyui0808'

DB_HOST = "ec2-54-155-200-16.eu-west-1.compute.amazonaws.com"
DB_USER = "ggxrwowcqvfbds"
DB_PASSWORD = "31f5bd629538e320403a8f258a569ea76c7c9fb72a10c77fa08b9b5eea82e960"
DB_NAME = "d2nrlcil3dbagd"
DB_URL = 'postgres://ggxrwowcqvfbds:31f5bd629538e320403a8f258a569ea76c7c9fb72a10c77fa08b9b5eea82e960@ec2-54-155-200-16.eu-west-1.compute.amazonaws.com:5432/d2nrlcil3dbagd'
