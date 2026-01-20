from .attacks_container import *
from .combat_container import *
from .header_container import *
from .information_container import *
from .stats_container import *


class PlayerSheet:
    def __init__(self):
        self.header_container = HeaderContainer()
        self.stats_container = StatsContainer()
        self.combat_container = CombatContainer()
        self.information_container = InformationContainer()
        self.attacks_and_spells = AttacksContainer()

    def __str__(self):
        return '\n'.join(str(item) for item in
                         (self.header_container, self.stats_container, self.combat_container, self.attacks_and_spells))

    def fill_header(self, ch_name, cls, pl_name, bg, algmt):
        self.header_container.set_char_name(ch_name)
        self.header_container.add_class(cls)
        self.header_container.set_player_name(pl_name)
        self.header_container.set_background(bg)
        self.header_container.set_allignment(algmt)

    def fill_stats(self):
        chars = []
        while len(chars) < 6:
            chars.extend([int(i) for i in ''.join([j for j in input() if (j.isdigit() or j == ' ')]).split()])
        for i in range(len(chars)):
            self.stats_container.stats.set_stat(i, chars[i])

    def register(self):
        self.fill_header()
        self.fill_stats()


class SheetsList:
    def __init__(self):
        self.__picked_sheets__ = dict()
        self.__users_sheets__ = dict()
        try:
            self.load()
        except Exception as e:
            print(f'Could not dump sheets data: {e}')

    def user_sheets(self, user: int):
        try:
            return self.__users_sheets__[user]
        except Exception:
            return None

    def picked_sheet(self, user: int):
        try:
            return self.__picked_sheets__[user]
        except Exception:
            return None

    def add_user_sheet(self, user: int, sheet: PlayerSheet):
        if user in self.__users_sheets__.keys():
            self.__users_sheets__[user].append(sheet)
        else:
            self.__users_sheets__[user] = [sheet]

    def remove_user_sheet(self, user: int, sheet: PlayerSheet):
        self.__users_sheets__[user].remove(sheet)

    def pick(self, user: int, sheet: PlayerSheet):
        self.__picked_sheets__[user] = sheet

    def dump(self):
        import json
        with open('data/sheets.json', 'w') as json_file:
            json.dump([self.__users_sheets__, self.__picked_sheets__], json_file, indent=4)

    def load(self):
        import json
        with open('data/sheets.json', 'r') as json_file:
            self.__users_sheets__, self.__picked_sheets__ = json.load(json_file)
        #TODO: playersheet serialization