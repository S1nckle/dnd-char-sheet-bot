class InformationContainer:
    def __init__(self):
        self.__personality = ''
        self.__ideals = ''
        self.__bonds = ''
        self.__flaws = ''

    def __str__(self):
        lines = [
            ' Информация '.center(50, '='),
            f'  Личность: ',
            self.__personality,
            f'  Идеалы: ',
            self.__ideals,
            f'  Связи: ',
            self.__bonds,
            f'  Слабости: ',
            self.__flaws
        ]
        return '\n'.join(lines)

    def to_dict(self):
        dct = {
            "personality": self.__personality,
            "ideals": self.__ideals,
            "bonds": self.__bonds,
            "flaws": self.__flaws
        }
        return dct

    def from_dict(self, dct: dict):
        self.__personality = dct["personality"]
        self.__ideals = dct["ideals"]
        self.__bonds = dct["bonds"]
        self.__flaws = dct["flaws"]

    def get_personality(self) -> str:
        return self.__personality

    def get_ideals(self) -> str:
        return self.__ideals

    def get_bonds(self) -> str:
        return self.__bonds

    def get_flaws(self) -> str:
        return self.__flaws

    def set_personality(self, descr: str):
        self.__personality = descr

    def set_ideals(self, descr: str):
        self.__ideals = descr

    def set_bonds(self, descr: str):
        self.__bonds = descr

    def set_flaws(self, descr: str):
        self.__flaws = descr

