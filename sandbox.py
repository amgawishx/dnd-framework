from jsonpickle import encode
from utils import load, save, fetchTable
from builds import Character, Race, Class
from mechanics import Feature, Spell, Slot, Ability
from features.functions import *

abilities = [Ability(score=13, name='str'),
             Ability(score=12, name='dex'),
             Ability(score=14, name='con'),
             Ability(score=15, name='int'),
             Ability(score=10, name='wis'),
             Ability(score=8, name='cha'),
             ]

healing_hands = Feature(name="Healing Hands",
                        function=healingHands, cost='1 action')
necrotic_shroud = Feature(name="Necrotic Shroud",
                          function=necroticShroud, cost='1 action')
rending_rite = Feature(name="Rending Rite",
                       function=rendingRite, cost='1 bonus action')
impute_rite = Feature(name="Impute Rite",
                      function=imputeRite, cost='1 bonus action')
mutual_suffering = Feature(name="Mutual Suffering",
                           function=mutualSuffering, cost='1 bonus action')

aasimar = Race(name="Aasimar (Fallen)", size="Medium", bonuses={'cha': 2, 'str': 1},
               languages=['common', 'celestial'], resistances=['necrotic', 'radiant'],
               spells=[load('spell', "Light")], speed=30, desc=None,
               features=[healing_hands, necrotic_shroud])

bloodhunter = Class(name="Bloodhunter", table=fetchTable("bloodhunter"), hit_dice="1d10",
                    proficiencies={
                        'Armor': ['light', 'medium'], 'weapons': ['simple', 'martial'],
                        'saves': ['dex', 'int'], 'tools': ['alchemist'],
                        'skills': ['Arcana', 'Investigation', 'Acrobatics']},
                    features=[impute_rite, mutual_suffering, rending_rite], level=3)

alexander = Character(name="Alexander", race=aasimar,
                      classes=[bloodhunter],
                      abilities=abilities,
                      background=load('background', 'Fallen Hero'),
                      ac=15, spellcaster=True,
                      spellcasting_ability='int')

alexander.max_hp = 36
alexander.current_hp = 36
alexander.slots[1] = Slot(1, 1)
save(alexander)

with open("alexander.json", "w") as file:
    file.write(encode(alexander))
