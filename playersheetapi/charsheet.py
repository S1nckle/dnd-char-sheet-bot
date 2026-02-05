import os

from .attacks_container import *
from .combat_container import *
from .header_container import *
from .information_container import *
from .stats_container import *
from .capabilities_container import *


class CharSheet:
    def __init__(self):
        self.header_container = HeaderContainer()
        self.stats_container = StatsContainer()
        self.combat_container = CombatContainer()
        self.information_container = InformationContainer()
        self.attacks_and_spells = AttacksContainer()

        self.profs_and_features = CapabilitiesContainer()

    def __str__(self):
        return '\n'.join(str(item) for item in
                         (self.header_container, self.stats_container, self.combat_container, self.attacks_and_spells,
                          self.information_container))

    def to_dict(self):
        dct = {
            "header": self.header_container.to_dict(),
            "stats": self.stats_container.to_dict(),
            "information": self.information_container.to_dict(),
            "combat": self.combat_container.to_dict(),
            "attacks": self.attacks_and_spells.to_dict(),
            "traits": self.profs_and_features.to_dict()
        }
        return dct

    @staticmethod
    def from_dict(dct: dict):
        c = CharSheet()
        c.header_container.from_dict(dct["header"])
        c.stats_container.from_dict(dct["stats"])
        c.information_container.from_dict(dct["information"])
        c.combat_container.from_dict(dct["combat"])
        c.attacks_and_spells.from_dict(dct["attacks"])
        c.profs_and_features.from_dict(dct["traits"])
        return c

    def fill_stats(self):
        chars = []
        while len(chars) < 6:
            chars.extend([int(i) for i in ''.join([j for j in input() if (j.isdigit() or j == ' ')]).split()])
        for i in range(len(chars)):
            self.stats_container.stats.set_stat(i, chars[i])


class SheetsList:
    def __init__(self):
        self.__users_sheets__ = dict()
        # Contains DISPLAYED NAMES and LINKS to sheets in values, user id in keys
        self.__picked_sheets__ = dict()
        # Contains single real LOADED sheet for each user with a LINK to its file in values

    def users_sheets(self, user: int) -> list:
        '''
        :param user: Users id
        :return: List of sheets assigned to user
        '''
        try:
            return self.__users_sheets__[user]
        except Exception:
            return None

    def add_users_sheet(self, user: int, sheet_name: str, sheet_file: str):
        sheet_register = {
            "name": sheet_name,
            "path": sheet_file
        }
        if user in self.__users_sheets__.keys():
            self.__users_sheets__[user].append(sheet_register)
        else:
            self.__users_sheets__[user] = [sheet_register, ]

    def remove_users_sheet(self, user: int, sheet_number: int):
        path = self.__users_sheets__[user].pop(sheet_number)["path"]
        if user in self.__picked_sheets__.keys():
            if self.picked_sheet(user)['path'] == path:
                self.__picked_sheets__['user'] = {}
        os.remove(path)

    def picked_sheet(self, user: int) -> dict[str, CharSheet]:
        '''
        :param user: Users id
        :return: Currently picked sheet by user
        '''
        try:
            return self.__picked_sheets__[user]
        except Exception:
            return None

    def pick(self, user: int, number: int):
        import json

        sheets = self.users_sheets(user)

        if number in range(len(sheets)):
            path = sheets[number]['path']
            file = open(path, 'r')
            sheet = CharSheet.from_dict(json.load(file))
            self.__picked_sheets__[user] = {
                'path': path,
                'sheet': sheet
            }
        else:
            raise ValueError(number)

    def create_sheet(self, user: int, sheet: CharSheet):
        import uuid
        import json
        import os

        unique_id = uuid.uuid4()
        # Check if id is already used (unlikely)
        if user in self.__users_sheets__.keys():
            while True:
                for item in self.__users_sheets__[user]:
                    if unique_id in item:
                        unique_id = uuid.uuid4()
                        break
                else:
                    break

        sheet_name = f'{sheet.header_container.get_char_name()}, {sheet.header_container.get_race()}' + \
                     f' {sheet.header_container.get_class(0)}'
        user_dir = f'data/saved_sheets/{user}/'
        file_name = f'{user_dir}{str(unique_id)}.json'
        self.add_users_sheet(user, sheet_name, file_name)

        os.makedirs(user_dir, exist_ok=True)

        with open(file_name, 'w+') as sheet_json:
            json.dump(sheet, sheet_json, default=lambda obj: obj.to_dict(), indent=4)

    def update_name(self, user: int, sheet: CharSheet, path: str):
        for s in self.__users_sheets__[user]:
            if s['path'] == path:
                s['name'] = f'{sheet.header_container.get_char_name()}, {sheet.header_container.get_race()}' + \
                     f' {sheet.header_container.get_class(0)}'

    def on_start(self):
        import os
        import json

        common_path = "data/common/"
        users_data_path = os.path.join(common_path, 'users_data.json')
        try:
            with open(users_data_path, 'r') as file:
                data = json.load(file)
                for user in data.keys():
                    self.__users_sheets__[int(user)] = data[user]
            print("Common data loaded successfully!")
        except Exception as e:
            print("Could not load common data:\n" + str(e))

    def on_close(self):
        import os
        import json

        common_path = "data/common/"
        users_data_path = os.path.join(common_path, 'users_data.json')

        os.makedirs(common_path, exist_ok=True)
        with open(users_data_path, 'w') as file:
            json.dump(self.__users_sheets__, file, indent=4)
        for user in self.__picked_sheets__.keys():
            with open(self.__picked_sheets__[user]['path'], 'w') as file:
                json.dump(self.__picked_sheets__[user]['sheet'], file, default=lambda obj: obj.to_dict(), indent=4)
            self.update_name(user, *self.__picked_sheets__[user])
