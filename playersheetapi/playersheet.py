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

    def fill_header(self):
        self.header_container.set_char_name(input('Введите имя героя: '))
        self.header_container.add_class(input('Введите первый класс: '))
        self.header_container.set_player_name(input('Введите имя игрока: '))
        self.header_container.set_background(input('Введите предысторию (Одним словом): '))
        self.header_container.set_allignment(input('Введите мировоззрение: '))

    def fill_stats(self):
        chars = []
        print('Введите значения характеристик по порядку: СИЛА, ЛОВКОСТЬ, ТЕЛОСЛОЖЕНИЕ, ИНТЕЛЛЕКТ, МУДРОСТЬ, ХАРИЗМА')
        while len(chars) < 6:
            chars.extend([int(i) for i in ''.join([j for j in input() if (j.isdigit() or j == ' ')]).split()])
        for i in range(len(chars)):
            self.stats_container.stats.set_stat(i, chars[i])
