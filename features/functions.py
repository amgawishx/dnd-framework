def necroticShroud(char: "Character", targets: list = None) -> None:
    char.misc_damages.append(
        {'roll': char.level, 'type': 'necrotic', 'multiplier': 1})
    if targets:
        for target in targets:
            saved = target.save('cha', char.dc)
            if not saved:
                target.setConditon('frightened')


def healingHands(character: "Character",
                 target: "Character") -> None:
    target.heal(character.level)


def imputeRite(character: "Character", weapon: 'Weapon', dtype: str) -> None:
    index = character.bag['weapons'].index(weapon)
    crimson_die = character.classes['Bloodhunter'].table[
        character.level]['Crimson Die']
    setattr(character.bag['weapons'][index], 'rite_imputed', True)
    character.bag['weapons'][index].damages.append({
        'roll': crimson_die,
        'type': dtype,
        'multiplier': 1,
        'rite': True
    })
    character.takeDamage(crimson_die, damage_type=None)


def rendingRite(character: "Character", weapon: 'Weapon',
                amplify=False) -> None:
    index = character.bag['weapons'].index(weapon)
    if amplify:
        character.takeDamage(
            character.classes['Bloodhunter'].table[
                character.level]['Crimson Die'],
            damage_type=None)
    dindex = None
    try:
        assert character.bag['weapons'][index].rite_imputed
        for damage in character.bag['weapons'][index].damages:
            try:
                damage['rite']
                dindex = character.bag['weapons'][index].damages.index(damage)
            except KeyError:
                pass
        character.bag['weapons'][index].damages[dindex]['multiplier'] = 2
    except AssertionError:
        print("Weapons is not imputed with rite!")


def mutualSuffering(character: "Character", amplify=False) -> None:
    multiplier = 1
    if amplify:
        character.takeDamage(
            character.classes['Bloodhunter'].table[
                character.level]['Crimson Die'],
            damage_type=None)
        multiplier = 2

    def reflectDamage(damage_info, multiplier):
        if 'necrotic' in damage_info['damager'].resistances and multiplier < 2:
            multiplier = 0.5
        damage_info['damager'].hp -= damage_info['damage']*multiplier
    try:
        character._events['get_hit'].subscribe(
            lambda x: reflectDamage(x, multiplier=multiplier))
    except KeyError:
        pass
