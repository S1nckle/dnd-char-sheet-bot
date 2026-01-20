from .dice import Dice


class AttackType:
    def __init__(self, name: str, hit: int, dmg_count: int, dmg_dice: int, dmg_type: str):
        self.__name = name
        self.__hit = hit
        self.__dmg_count = dmg_count
        self.__dmg_dice = Dice(dmg_dice)
        self.__dmg_type = dmg_type

    def __str__(self):
        return '      '.join((f'{self.__name}', f'{self.__hit:+}', f'{self.__dmg_count}{self.__dmg_dice}',
                              f'{self.__dmg_type}'))


class AttacksContainer:
    def __init__(self):
        self.__attacks = []

    def __str__(self):
        return ' Атаки '.center(50, '=') + '\n' + '\n'.join([str(item) for item in self.__attacks])

    def get_attacks(self):
        return self.__attacks

    def get_attack(self, index: int):
        if index in range(len(self.__attacks)):
            return self.__attacks[index]
        else:
            raise ValueError(index)

    def add_attack(self, attack: AttackType):
        self.__attacks.append(attack)

    def remove_attack(self, index: int):
        if index in range(len(self.__attacks)):
            self.__attacks.pop(index)
        else:
            raise ValueError(index)
