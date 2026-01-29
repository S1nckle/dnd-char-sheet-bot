from .dice import Dice


class DeathSaves:
    def __init__(self):
        self.__successes = [False, False, False]
        self.__failures = [False, False, False]

    def __str__(self):
        return 'Броски против смерти: '.center(50) + '\n' + \
            ('Успехи: ' + ' '.join(['●' if i else '○' for i in self.__successes]) + '\tНеудачи: ' + ' '.join(
                ['●' if i else '○' for i in self.__failures])).center(50)

    def to_dict(self):
        dct = {
            "successes": self.__successes,
            "failures": self.__failures
        }
        return dct

    def from_dict(self, dct: dict):
        self.__successes = dct["successes"]
        self.__failures = dct["failures"]


class CombatContainer:
    def __init__(self):
        self.__armor_class = 0
        self.__initiative = 0
        self.__speed = 0

        self.__hitpoints_max = 0
        self.__hitpoints = 0
        self.__temporary_hitpoints = 0
        self.__hitdice = Dice(0)
        self.__hitdice_count_max = 0
        self.__hitdice_count = 0

        self.__death_saves = DeathSaves()

    def __str__(self):
        initiative = f'{self.__initiative:+}'
        lines = [
            ' Бой '.center(50, '='),
            f"Класс доспеха:  {self.__armor_class:<8} Текущие хиты:      {self.__hitpoints:<8}",
            f"Инициатива:     {initiative:<8} Максимальные хиты: {self.__hitpoints_max:<8}",
            f"Скорость:       {self.__speed:<8} Временные хиты:    {self.__temporary_hitpoints:<8}",
            f"               {'':<8}  Кости хитов:       {self.__hitdice_count}{self.__hitdice}",
            str(self.__death_saves)
        ]

        return '\n'.join(lines)

    def to_dict(self):
        dct = {
            "armor_class": self.__armor_class,
            "initiative": self.__initiative,
            "speed": self.__speed,

            "hitpoints_max": self.__hitpoints_max,
            "hitpoints": self.__hitpoints,
            "temporary_hitpoints": self.__temporary_hitpoints,
            "hitdice": self.__hitdice.sides(),
            "hitdice_count_max": self.__hitdice_count_max,
            "hitdice_count": self.__hitdice_count,
            "death_saves": self.__death_saves.to_dict()
        }
        return dct

    def from_dict(self, dct: dict):
        self.__armor_class = dct["armor_class"]
        self.__initiative = dct["initiative"]
        self.__speed = dct["speed"]

        self.__hitpoints_max = dct["hitpoints_max"]
        self.__hitpoints = dct["hitpoints"]
        self.__temporary_hitpoints = dct["temporary_hitpoints"]

        self.__hitdice = Dice(dct["hitdice"])
        self.__hitdice_count = dct["hitdice_count"]
        self.__hitdice_count_max = dct["hitdice_count_max"]
        self.__death_saves.from_dict(dct["death_saves"])

    def get_armor_class(self) -> int:
        return self.__armor_class

    def set_armor_class(self, value: int):
        self.__armor_class = value

    def get_initiative(self) -> int:
        return self.__initiative

    def set_initiative(self, value: int):
        self.__initiative = value

    def get_speed(self) -> int:
        return self.__speed

    def set_speed(self, value: int):
        self.__speed = value

    def get_hitpoints(self) -> int:
        return self.__hitpoints

    def set_hitpoints(self, value: int):
        self.__hitpoints = value

    def get_max_hitpoints(self) -> int:
        return self.__hitpoints_max

    def set_max_hitpoints(self, value: int):
        self.__hitpoints_max = value

    def get_temporary_hitpoints(self) -> int:

        return self.__temporary_hitpoints

    def set_temporary_hitpoints(self, value: int):
        self.__temporary_hitpoints = value

    def hurt(self, damage: int):
        temp_damage = self.__temporary_hitpoints
        actual_damage = max(0, damage - temp_damage)
        self.__temporary_hitpoints -= temp_damage
        self.actually_hurt(actual_damage)

    def actually_hurt(self, damage: int):
        self.__hitpoints = max(0, self.__hitpoints - damage)

    def heal(self, heal: int):
        self.__hitpoints = min(self.__hitpoints_max, self.__hitpoints + heal)

    def get_hitdice(self) -> Dice:
        return self.__hitdice

    def set_hitdice(self, sides: int):
        if sides <= 0:
            raise ValueError(sides)
        self.__hitdice = Dice(sides)

    def get_hitdice_count(self) -> int:
        return self.__hitdice_count

    def set_hitdice_count(self, count: int):
        if count <= 0:
            raise ValueError(count)
        self.__hitdice_count = count
