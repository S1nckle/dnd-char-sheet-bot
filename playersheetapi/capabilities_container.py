class CapabilitiesContainer:
    def __init__(self):
        self.__proficiencies = []
        self.__features = []

    def __str__(self):
        lines = [
            ' Языки и владения '.center(50, '='),
            *self.__proficiencies,
            ' Черты и особенности '.center(50, '='),
            *self.__features
        ]
        return '\n'.join(lines)

    def to_dict(self):
        return {
            "profs": self.__proficiencies,
            "features": self.__features
        }

    def from_dict(self, dct: dict):
        self.__proficiencies = dct["profs"]
        self.__features = dct["features"]

    def add_prof(self, prof: str):
        self.__proficiencies.append(prof)

    def remove_prof(self, index: int):
        if index in range(len(self.__proficiencies)):
            self.__proficiencies.pop(index)

    def add_feature(self, feature: str):
        self.__features.append(feature)

    def remove_feature(self, index: int):
        if index in range(len(self.__features)):
            self.__features.pop(index)

    def proficiencies(self):
        return self.__proficiencies

    def features(self):
        return self.__features
