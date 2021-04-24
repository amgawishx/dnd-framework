from random import randint
from json import dumps, loads
import pickle

CONDITIONS = ['blinded', 'charmed', 'deafened', 'exhausted', 'frightened', 'grappled',
              'incapacitated', 'invisible', 'paralyzed', 'petrified', 'poisoned',
              'prone', 'restrained', 'stunned', 'concentraiting']

BASE_TABLE = {
    1: {'bonus': 2},
    2: {'bonus': 2},
    3: {'bonus': 2},
    4: {'bonus': 2},
    5: {'bonus': 3},
    6: {'bonus': 3},
    7: {'bonus': 3},
    8: {'bonus': 3},
    9: {'bonus': 4},
    10: {'bonus': 4},
    11: {'bonus': 4},
    12: {'bonus': 4},
    13: {'bonus': 5},
    14: {'bonus': 5},
    15: {'bonus': 5},
    16: {'bonus': 5},
    17: {'bonus': 6},
    18: {'bonus': 6},
    19: {'bonus': 6},
    20: {'bonus': 6},
}


def roll(str: str) -> int:
    bonus, sum, args = 0, 0, []
    str = str.replace(" ", "")

    def __roll(no, die):
        _sum = 0
        for _ in range(no):
            _sum += randint(1, die)
        return _sum

    def parseDie(die_str):
        splitted = die_str.split('d')
        return (int(splitted[0]), int(splitted[1]))
    rolls = str.split('+')
    for _roll in rolls:
        if 'd' not in _roll:
            bonus += int(_roll)
        else:
            args.append(parseDie(_roll))
    for arg in args:
        sum += __roll(*arg)
    return sum+bonus


def serialize(objects: list) -> dict:
    return {_object.name: _object for _object in objects}


def save(object: object) -> None:
    plular = 's'
    type_ = object.__class__.__name__.lower()
    if type_[::-1][0] == 's':
        plular = 'es'
    with open(f'./{type_}{plular}/{object.name}.pickle', 'wb') as file:
        pickle.dump(object, file)


def load(type: str, object_name: str) -> object:
    plular = 's'
    if type[::-1][0] == 's':
        plular = 'es'
    with open(f'./{type}{plular}/{object_name}.pickle', 'rb') as file:
        _object = pickle.load(file)
    return _object


def tableGenerator(table_name: str, no_of_columns: int) -> int:
    modified_table = BASE_TABLE
    for _ in range(no_of_columns):
        numerical = eval(input("Numerical Feautre (True or False)? "))
        name = input("Enter the feature name: ")
        for i in range(20):
            if numerical:
                modified_table[i+1][name] = eval(
                    input(f"Enter the feature at level {i+1}: "))
            else:
                modified_table[i+1][name] = input(
                    f"Enter the feature at level {i+1}: ")
    with open(f'./classes/tables/{table_name}.json', 'w') as file:
        file.write(dumps(modified_table))
    return 0


def fetchTable(name: str) -> dict:
    with open(f"./classes/tables/{name}.json", 'r') as table:
        table_str = ''.join(table.readlines())
        table_dict = loads(table_str)
        return table_dict
