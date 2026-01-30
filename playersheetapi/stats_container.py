from enum import IntEnum


class StatsEnum(IntEnum):
    STRENGTH = 0
    DEXTERITY = 1
    CONSTITUTION = 2
    INTELLIGENCE = 3
    WISDOM = 4
    CHARISMA = 5


class AbilitiesEnum(IntEnum):
    ACROBATICS = 0
    ANIMAL_HANDLING = 1
    ARCANA = 2
    ATHLETICS = 3
    DECEPTION = 4
    HISTORY = 5
    INSIGHT = 6
    INTIMIDATION = 7
    INVESTIGATION = 8
    MEDICINE = 9
    NATURE = 10
    PERCEPTION = 11
    PERFORMANCE = 12
    PERSUASION = 13
    RELIGION = 14
    SLEIGHT_OF_HAND = 15
    STEALTH = 16
    SURVIVAL = 17


class AbilitiesDict:
    __CONTENT = {
        StatsEnum.STRENGTH: [AbilitiesEnum.ATHLETICS],
        StatsEnum.DEXTERITY: [AbilitiesEnum.ACROBATICS, AbilitiesEnum.SLEIGHT_OF_HAND, AbilitiesEnum.STEALTH],
        StatsEnum.CONSTITUTION: [],
        StatsEnum.INTELLIGENCE: [AbilitiesEnum.ARCANA, AbilitiesEnum.HISTORY, AbilitiesEnum.INVESTIGATION, AbilitiesEnum.NATURE, AbilitiesEnum.RELIGION],
        StatsEnum.WISDOM: [AbilitiesEnum.ANIMAL_HANDLING, AbilitiesEnum.INSIGHT, AbilitiesEnum.MEDICINE, AbilitiesEnum.PERCEPTION, AbilitiesEnum.SURVIVAL],
        StatsEnum.CHARISMA: [AbilitiesEnum.DECEPTION, AbilitiesEnum.INTIMIDATION, AbilitiesEnum.PERFORMANCE, AbilitiesEnum.PERSUASION]
    }

    @staticmethod
    def get_stat(ability: int) -> int:
        for stat in AbilitiesDict.__CONTENT.keys():
            if ability in AbilitiesDict.__CONTENT[stat]:
                return stat
        raise ValueError(ability)


class StatsContainer:
    def __init__(self):
        self.stats = Stats()
        self.saving_throws = SavingThrows()
        self.abilities = Abilities()

    def __str__(self):
        saving_throws_modifiers = [self.stats.get_modifier(i) for i in self.stats.get_stats()]
        for i in range(len(saving_throws_modifiers)):
            saving_throws_modifiers[i] += self.saving_throws.get_saving_throw(i) * self.stats.get_proficiency()


        lines = [
            str(self.stats),
            ' Спасброски '.center(50, '='),
            f'  {self.__saving_throw_mark(StatsEnum.STRENGTH)}'
            f'        {self.__saving_throw_mark(StatsEnum.DEXTERITY)}'
            f'        {self.__saving_throw_mark(StatsEnum.CONSTITUTION)}'
            f'        {self.__saving_throw_mark(StatsEnum.INTELLIGENCE)}'
            f'        {self.__saving_throw_mark(StatsEnum.WISDOM)}'
            f'        {self.__saving_throw_mark(StatsEnum.CHARISMA)}',
            '   '.join((f'{i:+2d}'.center(6) for i in saving_throws_modifiers)).center(50)[1:],
            ' Навыки '.center(50, '='),
            ' Сила '.center(50),
            f'{self.__ability_mark(AbilitiesEnum.ATHLETICS)} Атлетика:          {self.get_ability_modifier(AbilitiesEnum.ATHLETICS):+2d}',
            ' Ловкость '.center(50),
            f'{self.__ability_mark(AbilitiesEnum.ACROBATICS)} Акробатика:        {self.get_ability_modifier(AbilitiesEnum.ACROBATICS):+2d}   '
            f'{self.__ability_mark(AbilitiesEnum.SLEIGHT_OF_HAND)} Ловкость рук:     {self.get_ability_modifier(AbilitiesEnum.SLEIGHT_OF_HAND)}',
            f'{self.__ability_mark(AbilitiesEnum.STEALTH)} Скрытность:        {self.get_ability_modifier(AbilitiesEnum.STEALTH):+2d}',
            ' Интеллект '.center(50),
            f'{self.__ability_mark(AbilitiesEnum.INVESTIGATION)} Анализ:            {self.get_ability_modifier(AbilitiesEnum.INVESTIGATION):+2d}   '
            f'{self.__ability_mark(AbilitiesEnum.HISTORY)} История:          {self.get_ability_modifier(AbilitiesEnum.HISTORY):+2d}',
            f'{self.__ability_mark(AbilitiesEnum.ARCANA)} Магия:             {self.get_ability_modifier(AbilitiesEnum.ARCANA):+2d}   '
            f'{self.__ability_mark(AbilitiesEnum.NATURE)} Природа:          {self.get_ability_modifier(AbilitiesEnum.NATURE):+2d}',
            f'{self.__ability_mark(AbilitiesEnum.RELIGION)} Религия:           {self.get_ability_modifier(AbilitiesEnum.RELIGION):+2d}',
            ' Мудрость '.center(50),
            f'{self.__ability_mark(AbilitiesEnum.PERCEPTION)} Восприятие:        {self.get_ability_modifier(AbilitiesEnum.PERCEPTION):+2d}   '
            f'{self.__ability_mark(AbilitiesEnum.SLEIGHT_OF_HAND)} Выживание:        {self.get_ability_modifier(AbilitiesEnum.SURVIVAL):+2d}',
            f'{self.__ability_mark(AbilitiesEnum.MEDICINE)} Медицина:          {self.get_ability_modifier(AbilitiesEnum.MEDICINE):+2d}   '
            f'{self.__ability_mark(AbilitiesEnum.SLEIGHT_OF_HAND)} Проницательность: {self.get_ability_modifier(AbilitiesEnum.INVESTIGATION):+2d}',
            f'{self.__ability_mark(AbilitiesEnum.ANIMAL_HANDLING)} Уход за животными: {self.get_ability_modifier(AbilitiesEnum.ANIMAL_HANDLING):+2d}',
            ' Харизма '.center(50),
            f'{self.__ability_mark(AbilitiesEnum.PERFORMANCE)} Выступление:       {self.get_ability_modifier(AbilitiesEnum.PERFORMANCE):+2d}   '
            f'{self.__ability_mark(AbilitiesEnum.INTIMIDATION)} Запугивание:      {self.get_ability_modifier(AbilitiesEnum.INTIMIDATION):+2d}',
            f'{self.__ability_mark(AbilitiesEnum.DECEPTION)} Обман:             {self.get_ability_modifier(AbilitiesEnum.DECEPTION):+2d}   '
            f'{self.__ability_mark(AbilitiesEnum.PERSUASION)} Убеждение:        {self.get_ability_modifier(AbilitiesEnum.PERSUASION):+2d}'

        ]
        return '\n'.join(lines)

    def to_dict(self):
        dct = {
            "stats": self.stats.to_dict(),
            "saving_throws": self.saving_throws.to_dict(),
            "abilities": self.abilities.to_dict(),
        }
        return dct

    def from_dict(self, dct: dict):
        self.stats.from_dict(dct["stats"])
        self.saving_throws.from_dict(dct["saving_throws"])
        self.abilities.from_dict(dct["abilities"])

    def __ability_mark(self, ability: int) -> str:
        return '●' if self.abilities.get_ability(ability) else '○'

    def __saving_throw_mark(self, throw: int) -> str:
        return '●' if self.saving_throws.get_saving_throw(throw) else '○'
    def get_ability_modifier(self, ability: int) -> int:
        return self.abilities.get_ability(ability) * self.stats.get_proficiency() + \
                    self.stats.get_modifier(self.stats.get_stat(AbilitiesDict.get_stat(ability)))


class Stats:
    def __init__(self):
        self.__proficiency = 2

        self.__stats = [8] * len(StatsEnum)

    def to_dict(self):
        dct = {
            "proficiency": self.__proficiency,
            "stats_list": self.__stats
        }
        return dct

    def from_dict(self, dct: dict):
        self.__proficiency = dct["proficiency"]
        self.__stats = dct["stats_list"]

    def get_stat(self, stat: int) -> int:
        if stat in range(len(self.__stats)):
            return self.__stats[stat]
        else:
            raise ValueError(stat)

    def get_stats(self):
        return self.__stats

    def get_proficiency(self):
        return self.__proficiency

    def set_stat(self, stat: int, value: int):
        if stat in range(len(self.__stats)):
            self.__stats[stat] = value
        else:
            raise ValueError(stat)

    def set_proficiency(self, value):
        self.__proficiency = value

    def get_modifier(self, stat: int) -> int:
        return (stat - 10) // 2

    def __str__(self):
        stats = self.get_stats()
        modifiers = [self.get_modifier(i) for i in self.get_stats()]
        stat_names = ['СИЛ', 'ЛВК', 'ТЕЛ', 'ИНТ', 'МДР', 'ХАР']

        lines = [
            ' Характеристики '.center(50, '='),
            '   '.join([f'{name:^6}' for name in stat_names]).center(50),
            '   '.join([f'{stat:^6}' for stat in stats]).center(50),
            '   '.join([f'{mod:+2d}'.center(6) for mod in modifiers]).center(50)[1:],
            f' Бонус владения: {self.get_proficiency()}'.center(50)
        ]

        return '\n'.join(lines)


class SavingThrows:
    def __init__(self):
        self.__saving_throws = [False] * len(StatsEnum)

    def to_dict(self):
        return self.__saving_throws

    def from_dict(self, dct: dict):
        self.__saving_throws = dct

    def get_saving_throw(self, stat: int) -> bool:
        if stat in range(len(self.__saving_throws)):
            return self.__saving_throws[stat]
        else:
            raise ValueError(stat)

    def set_saving_throw(self, stat: int, value: bool):
        if stat in range(len(self.__saving_throws)):
            self.__saving_throws[stat] = value
        else:
            raise ValueError(stat)


class Abilities:
    def __init__(self):
        self.__competencies = [False] * len(AbilitiesEnum)

    def to_dict(self):
        return self.__competencies

    def from_dict(self, dct: dict):
        self.__competencies = dct

    def get_ability(self, ability: int) -> bool:
        if ability in range(len(self.__competencies)):
            return self.__competencies[ability]
        else:
            raise ValueError(ability)

    def set_ability(self, ability: int, value: bool):
        if ability in range(len(self.__competencies)):
            self.__competencies[ability] = value
        else:
            raise ValueError(ability)

