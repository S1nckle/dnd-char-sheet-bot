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

    def to_dict(self):
        dct = {
            "name": self.__name,
            "hit": self.__hit,
            "dmg_count": self.__dmg_count,
            "dmg_dice": self.__dmg_dice.sides(),
            "dmg_type": self.__dmg_type
        }
        return dct

    @staticmethod
    def from_dict(dct: dict):
        name = dct["name"]
        hit = dct["hit"]
        dmg_count = dct["dmg_count"]
        dmg_dice = dct["dmg_dice"]
        dmg_type = dct["dmg_type"]
        return AttackType(name, hit, dmg_count, dmg_dice, dmg_type)



class AttacksContainer:
    def __init__(self):
        self.__attacks = []

    def __str__(self):
        return ' Атаки '.center(50, '=') + '\n' + '\n'.join([str(item) for item in self.__attacks])

    def to_dict(self):
        return [attack.to_dict() for attack in self.__attacks]

    def from_dict(self, dct: dict):
        for attack in dct:
            self.add_attack(AttackType.from_dict(dct[attack]))

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
