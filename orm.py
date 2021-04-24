from mechanics import Spell
from builds import Race
from requests import get
from json import loads

API = 'https://www.dnd5eapi.co/api/'


def fetchSpell(name: str) -> Spell:
    url = API + 'spells/'
    response = loads(get(url+name.lower()).text)
    try:
        response['damage']
    except KeyError:
        response['damage'] = {}
        response['damage']['damage_at_slot_level'] = None
        response['damage']['damage_type'] = None
    spell = Spell(
        name=response['name'],
        level=response['level'],
        damage=response['damage']['damage_at_slot_level'],
        damage_type=response['damage']['damage_type']['name'],
        components=response['components'],
        desc=response['desc'][0],
        school=response['school']['name'],
        check=response['dc']['dc_type']['name'].lower(),
        cost=response['casting_time'],
        concentration=response['concentration'],
    )
    return spell


def fetchRace(name: str) -> Race:
    url = API + 'races/'
    response = loads(get(url+name.lower()).text)
    traits, languages, bonuses, proficiencies = [], [], [], []
    for language in response['languages']:
        languages.append(language['name'])
    for trait in response['traits']:
        traits.append(trait['name'])
    for bonus in response['ability_bonuses']:
        bonuses.append(
            {'name': bonus['name'].lower(), 'bonus': bonus['bonus']})
    for proficiency in response['starting_proficiencies']:
        proficiencies.append(proficiency['name'])
    race = Race(
        name=response['name'],
        size=response['size'],
        bonuses=bonuses,
        languages=languages,
        speed=response['speed'],
        features=traits,
        pro=proficiencies,
    )
    return race
