class HeaderContainer:
    def __init__(self):
        self.__char_name = ''
        self.__class = []
        self.__level = []
        self.__background = ''
        self.__player_name = ''
        self.__race = ''
        self.__alignment = ''
        self.__exp = 0

    def __str__(self):
        lines = [
            ' Лист игрока '.center(50, '='),
            self.get_char_name() + (50 - len(self.get_char_name()) - len(str(self.get_exp()))) * ' ' + f'{self.get_exp()}',
            'Классы:        ' + ', '.join(f'{self.__class[i]} - {self.__level[i]}' for i in range(len(self.__class))),
            'Имя игрока:    ' + self.get_player_name(),
            'Раса:          ' + self.get_race(),
            'Происхождение: ' + self.get_background(),
            'Мировоззрение: ' + self.get_alignment(),
        ]
        return '\n'.join(lines)

    def to_dict(self):
        dct = {
            "char_name": self.__char_name,
            "class": self.__class,
            "level": self.__level,
            "background": self.__background,
            "player_name": self.__player_name,
            "race": self.__race,
            "alignment": self.__alignment,
            "experience": self.__exp
        }
        return dct

    def from_dict(self, dct: dict):
        self.__char_name = dct["char_name"]
        self.__class = dct["class"]
        self.__level = dct["level"]
        self.__background = dct["background"]
        self.__player_name = dct["player_name"]
        self.__race = dct["race"]
        self.__alignment = dct["alignment"]
        self.__exp = dct["experience"]


    def get_char_name(self):
        return self.__char_name

    def set_char_name(self, name: str):
        self.__char_name = name

    def get_class(self, number: int):
        if len(self.__class) == 0:
            return None
        if number in range(len(self.__class)):
            return self.__class[number]
        else:
            raise ValueError(number)

    def set_class(self, number: int, cls: str):
        if number in range(len(self.__class)):
            self.__class[number] = cls
        else:
            raise ValueError(number)

    def add_class(self, cls: str):
        self.__class.append(cls)
        self.__level.append(1)

    def get_class_count(self):
        return len(self.__class)

    def get_level(self, number: int) -> int:
        if number in range(len(self.__level)):
            return self.__level[number]
        else:
            raise ValueError(number)

    def set_level(self, number: int, value: int):
        if number in range(len(self.__level)):
             self.__level[number] = max(0, min(value, 20))
        else:
            raise ValueError(number)

    def remove_class(self, number: int):
        if number in range(len(self.__class)):
            self.__class.pop(number)
            self.__level.pop(number)
        else:
            raise ValueError(number)


    def levelup(self, number: int):
        if number in range(len(self.__level)):
            self.__level[number] += 1
        else:
            raise ValueError(number)

    def get_background(self) -> str:
        return self.__background

    def set_background(self, value: str):
        self.__background = value

    def get_player_name(self) -> str:
        return self.__player_name

    def set_player_name(self, value: str):
        self.__player_name = value

    def get_race(self) -> str:
        return self.__race

    def set_race(self, value: str):
        self.__race = value

    def get_alignment(self) -> str:
        return self.__alignment

    def set_alignment(self, value: str):
        self.__alignment = value

    def get_exp(self) -> int:
        return self.__exp

    def set_exp(self, value: int):
        self.__exp = value

    def gain_exp(self, value: int):
        self.__exp += value

