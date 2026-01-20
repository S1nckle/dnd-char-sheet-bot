class InformationContainer:
    def __init__(self):
        self.__personality = ''
        self.__ideals = ''
        self.__bonds = ''
        self.__flaws = ''

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

