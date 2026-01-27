import atexit

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from playersheetapi import *

file = open('bot_token.txt', 'r')
TOKEN = file.readline()
file.close()

# Global const
bot = telebot.TeleBot(TOKEN)
sheet_list = SheetsList()
sheet_list.on_start()
atexit.register(sheet_list.on_close)
PAGES_DATA = {}

'''
Callback codes (2-symbol hexadecimal prefixes + optional number):
    - 00X - pick command
        000 - pick sheet
        001 - change page
        002 - cancel
    - 01X - delete command
        010 - ask to delete
        011 - change page
        012 - actually delete
        013 - return to choosing
        014 - cancel
'''


### SHEET MANAGING ###
@bot.message_handler(commands=['start'])
def start_func(message):
    '''
        Приветственное сообщение
    '''
    user = message.from_user.id
    text = \
        '''Привет!
Этот бот создан для быстрого доступа к нескольким листам персонажа в цифровом формате.
Сейчас взглянем на твои листы...\n'''
    sls = sheet_list.users_sheets(user)
    if sls:
        text = text + f'У тебя есть {len(sls)} созданных листов!\nИспользуй команду /pick чтобы выбрать лист.'
    else:
        text = text + f'Кажется, у тебя еще нет созданных листов!\nПопробуй создать свой первый с помощью /create'
    bot.send_message(message.from_user.id, text=text)


@bot.message_handler(commands=['create'])
def create_sheet(message):
    sheet_list.create_sheet(message.from_user.id, CharSheet())
    bot.send_message(message.chat.id, text='Персонаж создан!')


@bot.message_handler(commands=['pick'])
def pick_sheet(message):
    users_sheets = sheet_list.users_sheets(message.from_user.id)

    if not users_sheets:
        bot.send_message(message.chat.id,
                         text='У тебя нет сохраненных листов! \nПопробуй создать свой с помощью /create')
        return

    user = message.from_user.id
    PAGES_DATA[user] = 0

    show_sheet_page(message.chat.id, message.from_user.id, 0)


def show_sheet_page(chat_id: int, user: int, page: int, edit_message=None, callback_code=0):
    """
        Send message with inline keyboard referring to users sheets, 5 per page
        :param edit_message: Edit message passed via this param instead of sending another
        :param callback_code: defines which command will catch the callback of keyboard

    """
    sheets = sheet_list.users_sheets(user)
    total_pages = (len(sheets) + 4) // 5

    start = page * 5
    end = min(start + 5, len(sheets))
    sheet_page = sheets[start:end]

    keyboard = []

    for sheet in sheet_page:
        num = page * 5
        if callback_code == 0:
            callback_data = f'000:{user}:{num}'
        elif callback_code == 1:
            callback_data = f'010:{user}:{num}'
        else:
            raise ValueError(callback_code)
        num += 1
        keyboard.append([InlineKeyboardButton(sheet['name'], callback_data=callback_data)])

    nav_row = []

    if page > 0:
        nav_row.append(InlineKeyboardButton('< Назад', callback_data=f'001:{user}:back'))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton('Вперед >', callback_data=f'011:{user}:forw'))

    if nav_row:
        keyboard.append(nav_row)

    if callback_code == 0:
        keyboard.append([InlineKeyboardButton('Отмена', callback_data=f'002')])
    elif callback_code == 1:
        keyboard.append([InlineKeyboardButton('Отмена', callback_data=f'014')])

    if not edit_message:
        bot.send_message(chat_id, text=f'Выбери лист (стр. {page + 1}/{total_pages})',
                         reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        bot.edit_message_text(chat_id=chat_id, message_id=edit_message,
                              text=f'Выбери лист (стр. {page + 1}/{total_pages})',
                              reply_markup=InlineKeyboardMarkup(keyboard))


@bot.callback_query_handler(func=lambda call: call.data.startswith('00'))
def handle_pick(call):
    data = call.data

    if data.startswith('000'):
        _, user, num = [int(i) for i in call.data.split(':')]
        sheet_list.pick(user, num)

        bot.edit_message_text(
            f'Лист выбран! Можешь открыть его с помощью /show_sheet или изменить с помощью /edit_sheet',
            chat_id=call.message.chat.id, message_id=call.message.id)
        bot.answer_callback_query(call.id)
        PAGES_DATA.pop(user)
    elif data.startswith('001'):
        _, user, direction = call.data.split(':')
        user = int(user)
        if direction == 'back':
            PAGES_DATA[user] = PAGES_DATA[user] - 1
        else:
            PAGES_DATA[user] = PAGES_DATA[user] + 1

        show_sheet_page(call.message.chat.id, int(user), PAGES_DATA[user], edit_message=call.message.id)
        bot.answer_callback_query(call.id)
    elif data.startswith('002'):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        PAGES_DATA.pop(call.from_user.id)
    else:
        bot.answer_callback_query(call.id, 'UNKNOWN COMMAND')


@bot.message_handler(commands=['delete'])
def delete_sheet(message):
    user = message.from_user.id
    users_sheets = sheet_list.users_sheets(user)

    if not users_sheets:
        bot.send_message(message.chat.id,
                         text='У тебя нет сохраненных листов! \nПопробуй создать свой с помощью /create')
        return

    PAGES_DATA[user] = 0

    show_sheet_page(message.chat.id, message.from_user.id, 0, callback_code=1)


@bot.callback_query_handler(func=lambda call: call.data.startswith('01'))
def handle_delete(call):
    data = call.data

    if data.startswith('010'):
        _, user, num = [int(i) for i in call.data.split(':')]
        keyboard = [[
            InlineKeyboardButton('Да', callback_data=f'012:{user}:{num}'),
            InlineKeyboardButton('Нет', callback_data=f'013:{user}')
        ]]
        bot.edit_message_text(
            text=f'Ты уверен, что хочешь удалить этот лист?\n{sheet_list.users_sheets(user)[num]["name"]}',
            chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=InlineKeyboardMarkup(keyboard))
        bot.answer_callback_query(call.id)

    elif data.startswith('011'):
        _, user, direction = call.data.split(':')
        user = int(user)
        if direction == 'back':
            PAGES_DATA[user] = PAGES_DATA[user] - 1
        else:
            PAGES_DATA[user] = PAGES_DATA[user] + 1

        show_sheet_page(call.message.chat.id, int(user), PAGES_DATA[user], edit_message=call.message.id,
                        callback_code=1)
        bot.answer_callback_query(call.id)
    elif data.startswith('012'):
        _, user, num = [int(i) for i in call.data.split(':')]
        sheet_list.remove_users_sheet(user, num)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Лист успешно удален.')
        PAGES_DATA.pop(user)
    elif data.startswith('013'):
        _, user = [int(i) for i in call.data.split(':')]
        print(PAGES_DATA)
        show_sheet_page(call.message.chat.id, user, PAGES_DATA[user], edit_message=call.message.id, callback_code=1)
    elif data.startswith('014'):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        PAGES_DATA.pop(call.from_user.id)
    else:
        bot.answer_callback_query(call.id, 'UNKNOWN COMMAND')


## SINGLE SHEET USE ###

@bot.message_handler(commands=['show_sheet'])
def show_sheet(message):
    user = message.from_user.id
    if not sheet_list.picked_sheet(user):
        bot.send_message(message.chat.id,
                         text='У тебя нет выбранного листа!\nВыбери один из своих листов с помощью /pick')
    bot.send_message(message.chat.id, text=str(sheet_list.picked_sheet(user)['sheet']))


if __name__ == '__main__':
    bot.infinity_polling()
