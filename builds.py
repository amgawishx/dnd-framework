from mechanics import Ability, Slot, Spell, Weapon, Feature
from typing import List, Dict, Union, Any
from utils import roll, dumps, serialize, CONDITIONS
from rx import create


class Race:
    def __init__(self, name: str, size: str, bonuses: Dict[str, int],
                 languages: List[str], resistances: List[str] = None,
                 spells: List[Spell] = None, speed: int = 30, desc: str = None,
                 features: List[Feature] = None, pro: dict = None):
        self.name = name
        self.size = size
        self.bonuses = bonuses
        self.languages = languages
        self.resistances = resistances
        self.speed = speed
        self.spells = spells
        self.features = features
        self.pro = pro

    def __str__(self) -> str:
        feature_names = [i for i in self.features.keys()]
        return f"""Name: {self.name}
Size: {self.size}
Languages: {self.languages}
Speed: {self.speed}
Abilities Bonuses: {dumps(self.bonuses, indent = 4, sort_keys = True)}
Proficiencies: {self.pro}
Features: {feature_names}
Resistances: {self.resistances}
"""


class Class:
    def __init__(self, name: str, table: dict, hit_dice: str,
                 proficiencies: Dict[str, List[str]],
                 features: Dict[str, Feature],
                 desc: str = None, level: int = None):
        self.name = name
        self.table = table
        self.hit_dice = hit_dice
        self.proficiencies = proficiencies
        self.features = features
        self.level = level
        self.desc = desc

    def __str__(self) -> str:
        return f"""
Name: {self.name}
Proficiencies: {self.proficiencies}
Hit Die: {self.hit_dice}
Table: {self.table}
--------
{self.desc}
"""


class Background:
    def __init__(self, name: str, proficiencies: Dict[str, List[str]],
                 languages: List[str], desc=None):
        self.name = name
        self.proficiencies = proficiencies
        self.languages = languages
        self.desc = desc

    def __str__(self) -> str:
        return f"""
Name: {self.name}
Skill Proficiencies: {self.proficiencies['skills']}
Tool Proficiencies: {self.proficiencies['tools']}
--------
{self.desc}
"""


class Character:
    def __init__(self, name: str, race: Race, classes: List[Class],
                 abilities: List[Ability], background: Background, ac: int,
                 spellcaster: bool = False, spellcasting_ability: str = None,
                 slots: Dict[int, Slot] = None, spells: Dict[str, Spell] = None,
                 conditions: List[str] = None, bag: Dict[str, list] = None,
                 vulnerabilities: List[str] = None, misc_damages: List[str] = None,
                 misc_resistances: List[str] = None, _events: list = None,
                 max_hp: int = None, current_hp: int = None):
        self.name = name
        self.race = race
        self.classes = (serialize(classes) if type(
            classes) == list else classes)
        self.background = background
        self.level = self.__computeLevel()
        self.pro_bonus = self.__calcProBonus()
        self.abilities = self.__computeProficiencies(abilities)
        if spellcaster:
            self.spellcaster = spellcaster
            self.spellcasting_ability = spellcasting_ability
            self.dc = self.__computeDC()
            self.slots = ({} if not slots else slots)
            self.spells = ({} if not spells else spells)
        self.max_hp = (self.__computeHP() if not max_hp else max_hp)
        self.current_hp = (self.max_hp if not current_hp else current_hp)
        self.ac = ac
        self.conditions = ([] if not conditions else conditions)
        self.bag = ({
            'weapons': [],
            'tools': [],
            'misc': [],
        } if not bag else bag)
        self.vulnerabilities = ([] if not vulnerabilities else vulnerabilities)
        self.misc_resistances = (
            [] if not misc_resistances else misc_resistances)
        self.misc_damages = ([] if not misc_damages else misc_damages)
        self._events = ({} if not _events else _events)
        self.__configureAttributes()

    def takeDamage(self, droll: str, dtype: str, multiplier: int = 1) -> None:
        if (dtype in self.race.resistances or
                dtype in self.misc_resistances):
            multiplier *= 0.5
        if (dtype in self.vulnerabilities):
            multiplier *= 2
        ### future condition-based code ###
        damage = round(roll(droll)*multiplier)
        self.current_hp -= damage
        print(f"Took {damage} {dtype} damage!")
        if self.current_hp < 0:
            self.current_hp = 0
            print("HP is now 0, death rolls are now active.")

    def setCondition(self, condition: str) -> None:
        try:
            assert condition in CONDITIONS
            self.conditions.append(condition)
            print(f"Sat to current conditions: {condition}.")
        except AssertionError:
            print("Error: unknown condition.")

    def save(self, ability_check, dc):
        rolled = roll('1d20') + self.abilities[ability_check].save
        saved = (rolled >= dc)
        if saved:
            print("Save succeeded!")
        else:
            print("Save failed.")
        return saved

    def heal(self, hp: int) -> None:
        self.current_hp = (self.current_hp + hp
                           if self.current_hp + hp <= self.max_hp
                           else self.max_hp)
        print(f"Healed {hp}!")

    def rollAttack(self, method: Union[Weapon, Spell],
                   target: 'Character', advantage=0,
                   misc_mod: str = None) -> None:
        types = {'melee': self.abilities['str'].mod+self.pro_bonus,
                 'ranged': self.abilities['dex']+self.pro_bonus}
        if isinstance(method, Spell):
            try:
                assert method.attack
            except AssertionError:
                print("Spell doesn't have attack attribute.")
            rolled = roll('1d20') + self.abilities[
                self.spellcasting_ability].mod + self.pro_bonus
            if advantage != 0:
                def _roll(): return roll('1d20') + self.abilities[
                    self.spellcasting_ability].mod + self.pro_bonus
                rolls = [_roll(), _roll()]
                rolled = (max(rolls) if advantage > 0 else min(rolls))
            if rolled >= target.ac:
                print("Attack succeeded!")
                target.takeDamage(
                    method.damage, method.damage_type)
                if self.misc_damages:
                    for damage in self.misc_damages:
                        target.takeDamage(damage['roll'],
                                          damage['type'], damage['multiplier'])
            else:
                print("Attack failed.")
        elif isinstance(method, Weapon):
            if not misc_mod:
                misc_mod = types[method.reach]
            rolled = roll('1d20') + misc_mod
            if advantage != 0:
                def _roll(): return roll('1d20') + misc_mod
                rolls = [_roll(), _roll()]
                rolled = (max(rolls) if advantage > 0 else min(rolls))
            if rolled >= target.ac:
                if self.misc_damages:
                    for damage in self.misc_damages:
                        target.takeDamage(damage['roll'],
                                          damage['type'], damage['multiplier'])
                for damage in method.damages:
                    target.takeDamage(damage['roll'],
                                      damage['type'], damage['multiplier'])
                print("Attack succeeded!")
            else:
                print("Attack failed.")

    def useFeature(self, location: str, name: str, target: 'Character' = None,
                   _input: Any = None) -> None:
        if location == 'race':
            self.race.features[name].use(target=target, _input=_input)
        else:
            self.classes[location].features[name].use(
                target=target, _input=_input)
        print(f"Used feature {name}")

    def update(self) -> None:
        self.__init__(self.name, self.race, list(self.classes.values()),
                      list(self.abilities.values()), self.background, self.ac,
                      self.spellcaster, self.spellcasting_ability, self.slots,
                      self.spells, self.conditions, self.bag, self.vulnerabilities,
                      self.misc_damages, self.misc_resistances, self._events, self.max_hp,
                      self.current_hp)

    def __computeLevel(self) -> int:
        level = 0
        for class_ in self.classes.values():
            level += class_.level
        return level

    def __calcProBonus(self) -> int:
        return round(1+self.level/4)

    def __computeProficiencies(self, abilities: List[Ability]) -> Dict[str, Ability]:
        new_abilities = []
        for i in range(6):
            if abilities[i].name in self.race.bonuses.keys():
                abilities[i].score += self.race.bonuses[abilities[i].name]
                abilities[i].update()
        for ability in abilities:
            old_abilities = new_abilities
            skills_set = set(Ability.types[ability.name])
            if (set(self.background.proficiencies['skills']) <= skills_set):
                save_pro = False
                for class_ in self.classes.values():
                    if ability.name in class_.proficiencies['saves']:
                        save_pro = True
                new_abilities.append(
                    Ability(score=ability.score, name=ability.name,
                            skills_pro=self.background.proficiencies['skills'],
                            pro=self.pro_bonus, save_pro=save_pro))
            else:
                for class_ in self.classes.values():
                    if (set(class_.proficiencies['skills']) <= skills_set):
                        save_pro = False
                        if ability.name in class_.proficiencies['saves']:
                            save_pro = True
                        new_abilities.append(
                            Ability(score=ability.score, name=ability.name,
                                    skills_pro=class_.proficiencies['skills'],
                                    pro=self.pro_bonus, save_pro=save_pro))
            if old_abilities == new_abilities:
                new_abilities.append(ability)
        return serialize(new_abilities)

    def __computeDC(self) -> int:
        return 8+self.abilities[self.spellcasting_ability].mod+self.pro_bonus

    def __computeHP(self) -> int:
        hp = 0
        higher_class_dc = '1d0'
        for key in self.classes.keys():
            if int(self.classes[key].hit_dice.split('d')[1]) > int(
                    higher_class_dc.split('d')[1]):
                higher_class_dc = self.classes[key].hit_dice
        for _ in range(self.level):
            hp += roll(higher_class_dc)
        return hp

    def __configureAttributes(self) -> None:
        for key in self.spells.keys():
            self.spells[key].caster = self
        self.race.features = (serialize(self.race.features)
                              if type(self.race.features) == list
                              else self.race.features)
        for key in self.race.features.keys():
            self.race.features[key].character = self
        for key in self.classes.keys():
            self.classes[key].features = (serialize(self.classes[key].features)
                                          if type(self.classes[key].features) == list
                                          else self.classes[key].features)
            for key2 in self.classes[key].features.keys():
                self.classes[key].features[key2].character = self

    def __str__(self) -> str:
        classes_names = [i for i in self.classes.keys()]
        first_line = f"Name: {self.name} | Class(es): {classes_names} | Race: {self.race.name}\n"
        first_dashes = len(first_line)
        third_line = f"Current HP: {self.current_hp} | AC: {self.ac} | DC: {self.dc}\n"
        third_dashes = len(third_line)
        second_line = f"Max HP: {self.max_hp} | Level: {self.level} | Proficiency: {self.pro_bonus}\n"
        second_dashes = len(second_line)
        ult_dashes = max([first_dashes, second_dashes, third_dashes])*'-'+"\n"
        lines = [first_line, ult_dashes, second_line,
                 ult_dashes, third_line, ult_dashes]
        return ''.join(lines)


class Monster(Character):
    def __init__(self):
        pass


class NPC(Character):
    def __init__(self):
        pass
