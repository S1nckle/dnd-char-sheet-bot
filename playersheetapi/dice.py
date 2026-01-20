class Dice:
    def __init__(self, sides: int):
        self.__sides = sides

    def throw(self) -> int:
        from random import randint
        return randint(1, self.__sides + 1)

    def throw_many(self, count: int) -> int:
        return sum(self.throw() for i in range(count))

    def __str__(self):
        return f'к{self.__sides}'
