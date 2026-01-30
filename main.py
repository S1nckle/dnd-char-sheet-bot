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
        :param callback_code: Defines which command will catch the callback of keyboard

    """
    sheets = sheet_list.users_sheets(user)
    total_pages = (len(sheets) + 4) // 5

    start = page * 5
    end = min(start + 5, len(sheets))
    sheet_page = sheets[start:end]

    keyboard = []
    num = page * 5
    for sheet in sheet_page:

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
            f'Лист выбран! Можешь открыть его с помощью /show или изменить с помощью /edit',
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
        show_sheet_page(call.message.chat.id, user, PAGES_DATA[user], edit_message=call.message.id, callback_code=1)
    elif data.startswith('014'):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        PAGES_DATA.pop(call.from_user.id)
    else:
        bot.answer_callback_query(call.id, 'UNKNOWN COMMAND')


### SINGLE SHEET USE ###

@bot.message_handler(commands=['show'])
def show(message):
    user = message.from_user.id
    if not sheet_list.picked_sheet(user):
        bot.send_message(message.chat.id,
                         text='У тебя нет выбранного листа!\nВыбери один из своих листов с помощью /pick')
        return
    bot.send_message(message.chat.id, text=f"""<pre>{str(sheet_list.picked_sheet(user)['sheet'])}</pre>""",
                     parse_mode='HTML')


@bot.message_handler(commands=['edit'])
def edit(message):
    user = message.from_user.id
    if not sheet_list.picked_sheet(user):
        bot.send_message(message.chat.id,
                         text='У тебя нет выбранного листа!\nВыбери один из своих листов с помощью /pick')
        return

    show_edit_menu(message.chat.id, user)


def show_edit_menu(chat_id, user_id, edit_message=None):
    keyboard = [
        [InlineKeyboardButton('Шапка', callback_data=f'021:{user_id}:header')],
        [InlineKeyboardButton('Характеристики', callback_data=f'021:{user_id}:stats')],
        [InlineKeyboardButton('Боевая информация', callback_data=f'021:{user_id}:combat')],
        [InlineKeyboardButton('Атаки', callback_data=f'021:{user_id}:attacks')],
        [InlineKeyboardButton('Информация', callback_data=f'021:{user_id}:info')],
        [InlineKeyboardButton('Отмена', callback_data=f'020:{user_id}')]
    ]
    if edit_message:
        bot.edit_message_text(chat_id=chat_id, message_id=edit_message, text='Что изменяем?',
                              reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        bot.send_message(chat_id=chat_id, text='Что изменяем?', reply_markup=InlineKeyboardMarkup(keyboard))


@bot.callback_query_handler(func=lambda call: call.data.startswith('02'))
def handle_edit(call):
    if call.data.startswith('020'):
        bot.delete_message(call.message.chat.id, call.message.id)
    elif call.data.startswith('021'):
        _, user, container = call.data.split(':')
        user = int(user)
        match container:
            case 'header':
                edit_header(call.message.chat.id, call.message.id, user)
            case 'stats':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Выбери часть: ',
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton('Характеристики', callback_data=f'029:{user}:stats')],
                                          [InlineKeyboardButton('Спасброски', callback_data=f'029:{user}:savings')],
                                          [InlineKeyboardButton('Навыки', callback_data=f'029:{user}:abilities')],
                                          [InlineKeyboardButton('Назад', callback_data=f'029:{user}:back')],
                                          [InlineKeyboardButton('Отмена', callback_data=f'020')],
                                      ]))
            case 'combat':
                edit_combat(call.message.chat.id, call.message.id, user)
            case 'attacks':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Что сделать?',
                                      reply_markup=(InlineKeyboardMarkup([
                                          [InlineKeyboardButton('Добавить', callback_data=f'027:{user}:add'),
                                           InlineKeyboardButton('Удалить', callback_data=f'027:{user}:del')],
                                          [InlineKeyboardButton('Назад', callback_data=f'027:{user}:back')],
                                          [InlineKeyboardButton('Отмена', callback_data=f'020')]
                                      ])))
            case 'info':
                edit_info(call.message.chat.id, call.message.id, user)
    elif call.data.startswith('022'):
        _, user, field = call.data.split(':')
        user = int(user)
        match field:
            case 'cancel':
                bot.delete_message(call.message.chat.id, call.message.id)
            case 'back':
                show_edit_menu(call.message.chat.id, user, edit_message=call.message.id)
            case 'class':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Что изменить?',
                                      reply_markup=InlineKeyboardMarkup(
                                          [[InlineKeyboardButton('Классы', callback_data=f'023:{user}:class')],
                                           [InlineKeyboardButton('Уровни', callback_data=f'023:{user}:level')],
                                           [InlineKeyboardButton('Назад', callback_data=f'021:{user}:header')],
                                           [InlineKeyboardButton('Отмена', callback_data=f'020')]]
                                      ))
            case _:
                handle_edit_field(call, user, field)
    elif call.data.startswith('023'):
        _, user, field = call.data.split(':')
        user = int(user)
        if field == 'level':
            keyboard = []
            header = sheet_list.picked_sheet(user)['sheet'].header_container
            for i in range(header.get_class_count()):
                keyboard.append([InlineKeyboardButton(f'{header.get_class(i)} - {header.get_level(i)}',
                                                      callback_data=f'026:{user}:{i}')])
            keyboard.append([InlineKeyboardButton('Назад', callback_data=f'022:{user}:class')])
            keyboard.append([InlineKeyboardButton('Отмена', callback_data='020')])
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Выбери класс: ',
                                  reply_markup=InlineKeyboardMarkup(keyboard))
        elif field == 'class':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Что сделать?',
                                  reply_markup=InlineKeyboardMarkup(
                                      [[InlineKeyboardButton('Добавить', callback_data=f'024:{user}:class:add')],
                                       [InlineKeyboardButton('Удалить', callback_data=f'024:{user}:class:del')],
                                       [InlineKeyboardButton('Назад', callback_data=f'022:{user}:class')],
                                       [InlineKeyboardButton('Отмена', callback_data=f'020')]]
                                  ))
    elif call.data.startswith('024'):
        _, user, field, mode = call.data.split(':')
        user = int(user)
        if mode == 'add':
            handle_edit_field(call, user, field)
        else:
            keyboard = []
            header = sheet_list.picked_sheet(user)['sheet'].header_container
            for i in range(header.get_class_count()):
                keyboard.append([InlineKeyboardButton(f'{header.get_class(i)} - {header.get_level(i)}',
                                                      callback_data=f'025:{user}:{i}')])
            keyboard.append([InlineKeyboardButton('Назад', callback_data=f'023:{user}:class')])
            keyboard.append([InlineKeyboardButton('Отмена', callback_data='020')])
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Выбери класс: ',
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    elif call.data.startswith('025'):
        _, user, id = [int(i) for i in call.data.split(':')]
        sheet_list.picked_sheet(user)['sheet'].header_container.remove_class(id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Класс удален.')
    elif call.data.startswith('026'):
        _, user, id = call.data.split(':')
        user = int(user)
        handle_edit_field(call, user, f'level:{id}')
    elif call.data.startswith('027'):
        _, user, command = call.data.split(':')
        user = int(user)
        if command == 'back':
            show_edit_menu(call.message.chat.id, user, edit_message=call.message.id)
        elif command == 'add':
            bot.send_message(chat_id=call.message.chat.id,
                             text='Напиши по порядку, разделив пробелами:\n<Название атаки> <Бонус попадания>' +
                                  ' <Количество> <Кость урона> <Тип урона>\nПробелы в названии замени на нижнее ' +
                                  'подчеркивание.\n Пример: \n Двуручный_меч +2 2 6 Рубящий')
            handle_edit_field(call, user, 'attack')
        elif command == 'del':
            attacks = sheet_list.picked_sheet(user)['sheet'].attacks_and_spells.get_attacks()
            keyboard = [[InlineKeyboardButton(text=str(attacks[i]), callback_data=f'028:{user}:{i}')] for i in
                        range(len(attacks))]
            keyboard.append([InlineKeyboardButton('Назад', callback_data=f'021:{user}:attacks')])
            keyboard.append([InlineKeyboardButton('Отмена', callback_data='020')])
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Выбери атаку: ',
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    elif call.data.startswith('028'):
        _, user, i = [int(i) for i in call.data.split(':')]
        sheet_list.picked_sheet(user)['sheet'].attacks_and_spells.remove_attack(i)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Атака удалена.')
    elif call.data.startswith('029'):
        _, user, field = call.data.split(':')
        user = int(user)

        if field == 'back':
            show_edit_menu(chat_id=call.message.chat.id, user_id=user, edit_message=call.message.id)
        elif field == 'stats':
            pass
        elif field == 'savings':
            edit_saving_throws(call.message.chat.id, call.message.id, user)
        elif field == 'abilities':
            edit_abilities(call.message.chat.id, call.message.id, user)
    elif call.data.startswith('02a'):
        user, id = [int(i) for i in call.data.split(':')[1:]]
        abilities = sheet_list.picked_sheet(user)['sheet'].stats_container.abilities
        abilities.set_ability(id, not abilities.get_ability(id))
        edit_abilities(call.message.chat.id, call.message.id, user)
    elif call.data.startswith('02b'):
        user, id = [int(i) for i in call.data.split(':')[1:]]
        throws = sheet_list.picked_sheet(user)['sheet'].stats_container.saving_throws
        throws.set_saving_throw(id, not throws.get_saving_throw(id))
        edit_saving_throws(call.message.chat.id, call.message.id, user)


def edit_header(chat_id, message_id, user_id):
    keyboard = [
        [InlineKeyboardButton('Имя персонажа', callback_data=f'022:{user_id}:char_name')],
        [InlineKeyboardButton('Классы', callback_data=f'022:{user_id}:class')],
        [InlineKeyboardButton('Имя игрока', callback_data=f'022:{user_id}:player_name')],
        [InlineKeyboardButton('Раса', callback_data=f'022:{user_id}:race')],
        [InlineKeyboardButton('Происхождение', callback_data=f'022:{user_id}:background')],
        [InlineKeyboardButton('Мировоззрение', callback_data=f'022:{user_id}:alignment')],
        [InlineKeyboardButton('Опыт', callback_data=f'022:{user_id}:exp')],
        [InlineKeyboardButton('Назад', callback_data=f'022:{user_id}:back')],
        [InlineKeyboardButton('Отмена', callback_data=f'022:{user_id}:cancel')],
    ]

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выбери поле: ',
                          reply_markup=InlineKeyboardMarkup(keyboard))


def edit_combat(chat_id, message_id, user_id):
    keyboard = [
        [InlineKeyboardButton('Класс доспеха', callback_data=f'022:{user_id}:ac')],
        [InlineKeyboardButton('Инициатива', callback_data=f'022:{user_id}:initiative')],
        [InlineKeyboardButton('Скорость', callback_data=f'022:{user_id}:speed')],
        [InlineKeyboardButton('Хиты', callback_data=f'022:{user_id}:hitpoints'),
         InlineKeyboardButton('Макс. хиты', callback_data=f'022:{user_id}:hitpoints_max')],
        [InlineKeyboardButton('Временные хиты', callback_data=f'022:{user_id}:hitpoints_temp')],
        [InlineKeyboardButton('Кость хитов', callback_data=f'022:{user_id}:hitdice'),
         InlineKeyboardButton('Число костей', callback_data=f'022:{user_id}:hitdice_count')]
    ]
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выбери поле: ',
                          reply_markup=InlineKeyboardMarkup(keyboard))


def edit_info(chat_id, message_id, user_id):
    keyboard = [
        [InlineKeyboardButton('Личность', callback_data=f'022:{user_id}:personality')],
        [InlineKeyboardButton('Идеалы', callback_data=f'022:{user_id}:ideals')],
        [InlineKeyboardButton('Связи', callback_data=f'022:{user_id}:bonds')],
        [InlineKeyboardButton('Слабости', callback_data=f'022:{user_id}:flaws')],
        [InlineKeyboardButton('Отмена', callback_data=f'020')],
    ]

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выбери поле: ',
                          reply_markup=InlineKeyboardMarkup(keyboard))


def edit_saving_throws(chat_id, message_id, user_id):
    stats_container = sheet_list.picked_sheet(user_id)['sheet'].stats_container
    throws = stats_container.saving_throws

    def marker(throw: int) -> str:
        return '● ' if throws.get_saving_throw(throw) else '○ '

    keyboard = [
        [InlineKeyboardButton(f'{marker(StatsEnum.STRENGTH)}Сила '
                              f'({stats_container.get_saving_throw_modifier(StatsEnum.STRENGTH):+})',
                              callback_data=f'02b:{user_id}:{StatsEnum.STRENGTH}')],
        [InlineKeyboardButton(f'{marker(StatsEnum.DEXTERITY)}Ловкость '
                              f'({stats_container.get_saving_throw_modifier(StatsEnum.DEXTERITY):+})',
                              callback_data=f'02b:{user_id}:{StatsEnum.DEXTERITY}')],
        [InlineKeyboardButton(f'{marker(StatsEnum.CONSTITUTION)}Телосложение '
                              f'({stats_container.get_saving_throw_modifier(StatsEnum.CONSTITUTION):+})',
                              callback_data=f'02b:{user_id}:{StatsEnum.CONSTITUTION}')],
        [InlineKeyboardButton(f'{marker(StatsEnum.INTELLIGENCE)}Интеллект '
                              f'({stats_container.get_saving_throw_modifier(StatsEnum.INTELLIGENCE):+})',
                              callback_data=f'02b:{user_id}:{StatsEnum.INTELLIGENCE}')],
        [InlineKeyboardButton(f'{marker(StatsEnum.WISDOM)}Мудрость '
                              f'({stats_container.get_saving_throw_modifier(StatsEnum.WISDOM):+})',
                              callback_data=f'02b:{user_id}:{StatsEnum.WISDOM}')],
        [InlineKeyboardButton(f'{marker(StatsEnum.CHARISMA)}Харизма '
                              f'({stats_container.get_saving_throw_modifier(StatsEnum.CHARISMA):+})',
                              callback_data=f'02b:{user_id}:{StatsEnum.CHARISMA}')],
        [InlineKeyboardButton(f'Назад', callback_data=f'021:{user_id}:stats')],
        [InlineKeyboardButton(f'Отмена', callback_data=f'020')],
    ]
    bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text='Выбери спасбросок, который нужно получить/убрать',
                          reply_markup=InlineKeyboardMarkup(keyboard))


def edit_abilities(chat_id, message_id, user_id):
    stats_container = sheet_list.picked_sheet(user_id)['sheet'].stats_container
    abilities = stats_container.abilities

    def marker(ability: int) -> str:
        return '● ' if abilities.get_ability(ability) else '○ '

    keyboard = [
        [InlineKeyboardButton(
            f'{marker(AbilitiesEnum.ATHLETICS)}Атлетика ' +
            f'({stats_container.get_ability_modifier(AbilitiesEnum.ATHLETICS):+})',
            callback_data=f'02a:{user_id}:{AbilitiesEnum.ATHLETICS}')],
        [InlineKeyboardButton(f'{marker(AbilitiesEnum.ACROBATICS)}Акробатика ' +
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.ACROBATICS):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.ACROBATICS}'),
         InlineKeyboardButton(f'{marker(AbilitiesEnum.SLEIGHT_OF_HAND)}Ловкость рук '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.SLEIGHT_OF_HAND):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.SLEIGHT_OF_HAND}')],
        [InlineKeyboardButton(f'{marker(AbilitiesEnum.STEALTH)}Скрытность '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.STEALTH):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.STEALTH}')],
        [InlineKeyboardButton(f'{marker(AbilitiesEnum.INSIGHT)}Анализ '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.INSIGHT):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.INSIGHT}'),
         InlineKeyboardButton(f'{marker(AbilitiesEnum.HISTORY)}История '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.HISTORY):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.HISTORY}')],
        [InlineKeyboardButton(f'{marker(AbilitiesEnum.ARCANA)}Магия '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.ARCANA):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.ARCANA}'),
         InlineKeyboardButton(f'{marker(AbilitiesEnum.NATURE)}Природа '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.NATURE):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.NATURE}')],
        [InlineKeyboardButton(f'{marker(AbilitiesEnum.RELIGION)}Религия '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.RELIGION):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.RELIGION}')],
        [InlineKeyboardButton(f'{marker(AbilitiesEnum.PERCEPTION)}Восприятие '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.PERCEPTION):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.PERCEPTION}'),
         InlineKeyboardButton(f'{marker(AbilitiesEnum.SURVIVAL)}Выживание '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.SURVIVAL):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.SURVIVAL}')],
        [InlineKeyboardButton(f'{marker(AbilitiesEnum.MEDICINE)}Медицина '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.MEDICINE):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.MEDICINE}'),
         InlineKeyboardButton(f'{marker(AbilitiesEnum.INVESTIGATION)}Проницательность '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.INVESTIGATION):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.INVESTIGATION}')],
        [InlineKeyboardButton(f'{marker(AbilitiesEnum.ANIMAL_HANDLING)}Уход за животными '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.ANIMAL_HANDLING):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.ANIMAL_HANDLING}')],
        [InlineKeyboardButton(f'{marker(AbilitiesEnum.PERFORMANCE)}Выступление '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.PERFORMANCE):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.PERFORMANCE}'),
         InlineKeyboardButton(f'{marker(AbilitiesEnum.INTIMIDATION)}Запугивание '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.INTIMIDATION):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.INTIMIDATION}')],
        [InlineKeyboardButton(f'{marker(AbilitiesEnum.DECEPTION)}Обман '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.DECEPTION):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.DECEPTION}'),
         InlineKeyboardButton(f'{marker(AbilitiesEnum.PERSUASION)}Убеждение '
                              f'({stats_container.get_ability_modifier(AbilitiesEnum.PERSUASION):+})',
                              callback_data=f'02a:{user_id}:{AbilitiesEnum.PERSUASION}')],
        [InlineKeyboardButton('Назад', callback_data=f'021:{user_id}:stats')],
        [InlineKeyboardButton('Отмена', callback_data=f'020')],
    ]
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Выбери навык, который нужно получить/убрать.',
                          reply_markup=InlineKeyboardMarkup(keyboard))


def handle_edit_field(call, user, field):
    chat_id = call.message.chat.id
    message_id = call.message.id

    if not hasattr(handle_edit_field, 'waiting_users'):
        handle_edit_field.waiting_users = {}
    handle_edit_field.waiting_users[user] = field
    bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text=f'Введи новое значение: \n(cancel/отмена чтобы отменить)')


@bot.message_handler(func=lambda message: True)
def actually_edit(message):
    user = message.from_user.id

    if hasattr(handle_edit_field, 'waiting_users') and user in handle_edit_field.waiting_users:
        field = handle_edit_field.waiting_users[user]
        del handle_edit_field.waiting_users[user]

        if message.text.lower() in ('cancel', 'отмена'):
            bot.send_message(chat_id=message.chat.id, text='Изменение отменено')
            return

        sheet = sheet_list.picked_sheet(user)['sheet']

        match field:
            case 'char_name':
                sheet.header_container.set_char_name(message.text)
            case 'player_name':
                sheet.header_container.set_player_name(message.text)
            case 'class':
                sheet.header_container.add_class(message.text)
            case 'race':
                sheet.header_container.set_race(message.text)
            case 'background':
                sheet.header_container.set_background(message.text)
            case 'alignment':
                sheet.header_container.set_alignment(message.text)
            case 'exp':
                if message.text.isdigit():
                    sheet.header_container.set_exp(int(message.text))
                else:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    return

            case 'ac':
                if message.text.isdigit():
                    sheet.combat_container.set_armor_class(int(message.text))
                else:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    return
            case 'initiative':
                if message.text.isdigit() or (message.text[0] in '+-' and message.text[1:].isdigit):
                    sheet.combat_container.set_initiative(int(message.text))
                else:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    return
            case 'speed':
                if message.text.isdigit():
                    sheet.combat_container.set_speed(int(message.text))
                else:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    return
            case 'hitpoints':
                if message.text.isdigit():
                    sheet.combat_container.set_hitpoints(int(message.text))
                else:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    return
            case 'hitpoints_max':
                if message.text.isdigit():
                    sheet.combat_container.set_max_hitpoints(int(message.text))
                else:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    return
            case 'hitpoints_temp':
                if message.text.isdigit():
                    sheet.combat_container.set_temporary_hitpoints(int(message.text))
                else:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    return
            case 'hitpoints_temp':
                if message.text.isdigit():
                    sheet.combat_container.set_temporary_hitpoints(int(message.text))
                else:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    return
            case 'hitdice':
                if message.text.isdigit():
                    sheet.combat_container.set_hitdice(int(message.text))
                else:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    return
            case 'hitdice_count':
                if message.text.isdigit():
                    sheet.combat_container.set_hitdice_count(int(message.text))
                else:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    return
            case 'attack':
                try:
                    name, hit, hitdice, count, type = message.text.split()
                    name = name.replace('_', ' ')
                    hit, hitdice, count = int(hit), int(hitdice), int(count)
                    a = AttackType(name, hit, hitdice, count, type)
                    sheet.attacks_and_spells.add_attack(a)
                except Exception as e:
                    bot.send_message(message.chat.id, text='Неверное значение.')
                    print('Не вышло записать новую атаку: ', e)
                    return

            case 'personality':
                sheet.information_container.set_personality(message.text)
            case 'ideals':
                sheet.information_container.set_ideals(message.text)
            case 'bonds':
                sheet.information_container.set_bonds(message.text)
            case 'flaws':
                sheet.information_container.set_flaws(message.text)

        # Special fields requiring its own handle
        if field.startswith('level'):
            if message.text.isdigit():
                sheet.header_container.set_level(int(field.split(':')[-1]), int(message.text))
            else:
                bot.send_message(message.chat.id, text='Неверное значение.')

        sheet_list.update_name(user, sheet, sheet_list.picked_sheet(user)['path'])
        bot.send_message(message.chat.id, text='Поле успешно изменено!')


if __name__ == '__main__':
    bot.infinity_polling()
