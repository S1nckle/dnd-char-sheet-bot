import atexit

import telebot

from playersheetapi import *

file = open('bot_token.txt', 'r')
TOKEN = file.readline()
file.close()

bot = telebot.TeleBot(TOKEN)
sheet_list = SheetsList()

atexit.register(sheet_list.dump)


@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user.id
    text = \
        '''Привет!
Этот бот создан для быстрого доступа к нескольким листам персонажа в цифровом формате.
Сейчас взглянем на твои листы...\n'''
    sls = sheet_list.user_sheets(user)
    if sls:
        text = text + f'У тебя есть {len(sls)} созданных листов!\nИспользуй команду /pick чтобы выбрать лист.'
    else:
        text = text + f'Кажется, у тебя еще нет созданных листов!\nПопробуй создать свой первый с помощью /create'
    bot.send_message(message.from_user.id, text=text)


@bot.message_handler(commands=['create'])
def create_sheet(message):
    sheet_list.add_user_sheet(message.from_user.id, PlayerSheet())
    sheet_list.pick(message.from_user.id, sheet_list.user_sheets(message.from_user.id)[0])
    bot.send_message(message.from_user.id, text='Персонаж создан!')


if __name__ == '__main__':
    bot.infinity_polling()
