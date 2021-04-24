from utils import dumps, roll


class Ability:
    def __init__(self, score: int, name: str,
                 pro: int = 0, save_pro: bool = False,
                 skills_pro: list = None, advantage: int = 0):
        if not skills_pro:
            skills_pro = []
        self.advantage = advantage
        self._skills_pro = skills_pro
        self._save_pro = save_pro
        self._pro = pro
        self.score = score
        self.name = name
        self.mod = self.__calcMod()
        self.save = (self.mod + pro if save_pro else self.mod)
        self.skills = {}
        for skill in Ability.types[name]:
            if skill in skills_pro:
                self.skills[skill] = self.mod + pro
            else:
                self.skills[skill] = self.mod

    def update(self) -> None:
        self.__init__(self.score, self.name, self._pro,
                      self._save_pro, self._skills_pro)

    def __calcMod(self) -> int:
        return round((self.score-10)/2)

    types = {
        'str': ['Athletics'],
        'dex': ['Acrobatics', 'Sleight of Hand', 'Stealth'],
        'int': ['Arcana', 'History', 'Investigation', 'Nature', 'Religion'],
        'con': [],
        'wis': ['Animal Handling', 'Insight', 'Medicine',
                'Perception', 'Survival'],
        'cha': ['Deception', 'Intimidation', 'Performance', 'Persuasion'],
    }

    def __str__(self) -> str:
        return f"""Type: {self.name}
Score: {self.score}
Modifier: {self.mod}
Save: {self.save}
Skills: {dumps(self.skills, indent = 4, sort_keys = True)}
"""


class Slot:
    def __init__(self, level: int, uses: int):
        self.level = level
        self._uses = uses
        self.uses = uses

    def consume(self, times: int = 1) -> None:
        try:
            self.uses -= 1*times
            assert self.uses >= 0
        except AssertionError:
            print("No enough uses!")

    def replenish(self) -> None:
        self.uses = self._uses

    def gain(self, no: int) -> None:
        self.uses += no


class Spell:
    def __init__(self, name: str, level: int,
                 damage: dict = None, condition: str = None,
                 check: str = None, concentration: bool = False,
                 desc: str = None, attack: str = None,
                 components: list = None, damage_type: str = None,
                 school: str = None, dc: int = None, heal_roll: str = None,
                 cost: str = '1 action', caster: 'Character' = None):
        self.name = name
        self.level = level
        self.concentration = concentration
        self.damage = damage
        self.condition = condition
        self.check = check
        self.desc = desc
        self.components = components
        self.damage_type = damage_type
        self.school = school
        self.dc = dc
        self.cost = cost
        self.attack = attack
        self.caster = caster
        self.heal_roll = heal_roll

    def cast(self, slot_level: int,
             target: 'Character' = None) -> None:
        try:
            assert self.caster
        except:
            raise Warning("No caster specified for the spell!")
        if not self.dc:
            self.dc = self.caster.dc
        try:
            assert slot_level >= self.level
            assert self.caster.slots[slot_level].uses > 0
            self.caster.slots[slot_level].consume()
            if target:
                saved = target.save(self.check, self.dc)
                if self.damage_type:
                    multiplier = 1
                    if saved:
                        multiplier = 0.5
                    target.takeDamage(
                        self.damage[str(slot_level)], self.damage_type,
                        multiplier=multiplier)
                    if self.caster.misc_damages:
                        for damage in self.caster.misc_damages:
                            target.takeDamage(damage['roll'],
                                              damage['type'],
                                              damage['multiplier'])
                if self.condition:
                    if not saved:
                        target.setCondition(self.condition)
                if self.heal_roll:
                    target.heal(roll(self.heal_roll))
            if self.concentration:
                self.caster.setCondition('concentrating')
            if self.condition and not target:
                self.caster.setCondition(self.condition)
        except AssertionError:
            print("No enough uses available for that slot or slot level is too low.")
            return None

    def __str__(self) -> str:
        return f"""{self.name} (Level {self.level})
School: {self.school}
Components: {self.components}
{self.desc}
"""


class Weapon:
    def __init__(self, _type: str, name: str, damages: list, reach: str,
                 properties: list = None, magical: bool = False):
        self.name = name
        self.magical = magical
        self.type = _type
        self.name = name
        self.damages = damages
        self.properties = properties
        self.reach = reach

    def __str__(self) -> str:
        return self.name


class Feature:
    def __init__(self, name: str, function: 'function', cost: str = None,
                 char: 'Character' = None, desc: str = None):
        self.name = name
        self.function = function
        self.cost = cost
        self.character = char
        self.desc = desc

    def use(self, target: 'Character' = None, _input: 'Any' = None) -> None:
        try:
            assert self.character
        except AssertionError:
            raise Warning("No owner character specified!")
        if target:
            if _input:
                self.function(self.character, target, *_input)
            else:
                self.function(self.character, target)
        else:
            if _input:
                self.function(self.character, *_input)
            else:
                self.function(self.character)

    def __str__(self):
        return f"{self.name}: {self.desc}"
