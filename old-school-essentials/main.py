# main.py

import argparse
import os
import contextlib

import d20
from jinja2 import Environment, FileSystemLoader

from constants import *


csTemplate = 'template.pdf'
csOutput = 'characterSheet.pdf'

statRoll = '3d6'

def baseStats(character):
    character['Level'] = 1
    character['Equipment'] = ''#Backpack\nLantern\nFlask of Oil (5)\nJug of Ale (1)\nRations (7 days)\nLarge Sack\nWaterskin'
    character['XP'] = 0

def chooseClass(character):
    character['class'] = CLASS_OPTIONS[d20.roll('d7').total - 1]
    character['Listen at Door'] = CLASS_LISTEN[character['class']]
    character['Find Secret Door'] = CLASS_SECRET_DOOR[character['class']]
    character['Find Room Trap'] = CLASS_ROOM_TRAP[character['class']]
    character['xp_to_level'] = CLASS_XP_TO_LEVEL[character['class']]
    character['display_class'] = CLASS_DISPLAY[character['class']]

def chooseArmor(character):
    availableArmor = CLASS_ARMOR_OPTIONS[character['class']]

    roll = '1d' + str(len(availableArmor))

    character['armor'] = availableArmor[d20.roll(roll).total - 1]

    character['Weapons and Armour'] = character['armor'] + '\n'
    character['AC'] = ARMOR_CLASS[character['armor']] - character['dex_ac_mod']
    
    character['hasShield'] = False

    if CLASS_SHIELD[character['class']]:
        if d20.roll('1d2').total == 1:
            character['Weapons and Armour'] += 'Shield\n'
            character['AC'] = character['AC'] - 1
            character['hasShield'] = True

    character['exp_movement'] = ARMOR_BASE_MOVE[character['armor']]
    character['Overland Movement'] = int(ARMOR_BASE_MOVE[character['armor']] / 5)
    character['Encounter Movement'] = int(ARMOR_BASE_MOVE[character['armor']] / 3)

def chooseWeapon(character):
    availableWeapons = CLASS_WEAPONS[character['class']][character['hasShield']]

    selected = availableWeapons[d20.roll('1d' + str(len(availableWeapons))).total - 1]

    character['weapon'] = selected
    character['damage'] = WEAPON_DAMAGE[selected]
    character['Weapons and Armour'] += selected + ' (' + character['damage'] + ')\n'

    character['GP'] = character['GP'] - WEAPON_COST[character['weapon']]

def statsValidForClass(character):
    if character['class'] not in CLASS_REQS.keys():
        return True
    else:
        reqs = CLASS_REQS[character['class']]

        result = True

        for stat in reqs.keys():
            result = result & (character[stat] >= reqs[stat])

        return result

def chooseStats(character):
    rollStats(character)

    while not statsValidForClass(character):
        rollStats(character)

def rollStats(character):
    character['STR'] = d20.roll(statRoll).total
    character['INT'] = d20.roll(statRoll).total
    character['DEX'] = d20.roll(statRoll).total
    character['WIS'] = d20.roll(statRoll).total
    character['CON'] = d20.roll(statRoll).total
    character['CHA'] = d20.roll(statRoll).total

def noteMods(character):
    character['str_melee_mod'] = STANDARD_BONUS[character['STR']]
    character['Open Stuck Door'] = STR_OPEN_DOORS[character['STR']]
    character['Languages'] = INT_LANGUAGES[character['INT']]
    character['Literacy'] = INT_LITERACY[character['INT']]
    character['dex_ac_mod'] = STANDARD_BONUS[character['DEX']]
    character['Unarmoured AC'] = 9 - character['dex_ac_mod']
    character['Dex Missile Mod'] = STANDARD_BONUS[character['DEX']]
    character['Initiative DEX Mod'] = ALTERNATIVE_BONUS[character['DEX']]
    character['reactions_cha_mod'] = ALTERNATIVE_BONUS[character['CHA']]
    character['magic_save_mod'] = STANDARD_BONUS[character['WIS']]
    character['con_hp_mod'] = STANDARD_BONUS[character['CON']]

def determineAttack(character):
    melee = WEAPON_MELEE[character['weapon']]

    bonus = character['str_melee_mod'] if melee else 0

    character['THAC0'] = 19 - bonus
    character['THAC1'] = 18 - bonus
    character['THAC2'] = 17 - bonus
    character['THAC3'] = 16 - bonus
    character['THAC4'] = 15 - bonus
    character['THAC5'] = 14 - bonus
    character['THAC6'] = 13 - bonus
    character['THAC7'] = 12 - bonus
    character['THAC8'] = 11 - bonus
    character['THAC9'] = 10 - bonus

def noteSavingThrows(character):
    character['SAVING_THROWS'] = SAVING_THROWS[character['class']]
    character['Death_Save'] = character['SAVING_THROWS'][0]
    character['Wands_Save'] = character['SAVING_THROWS'][1]
    character['Paralysis_Save'] = character['SAVING_THROWS'][2]
    character['Breath_Save'] = character['SAVING_THROWS'][3]
    character['Spells_Save'] = character['SAVING_THROWS'][4]

def rollHp(character):
    character['HD'] = CLASS_HD[character['class']]
    character['Max HP'] = d20.roll(character['HD']).total + character['con_hp_mod']

    if character['Max HP'] < 1:
        character['Max HP'] = 1

    character['HP'] = character['Max HP']

def chooseAlignment(character):
    character['Alignment'] = ALIGNMENT_OPTIONS[d20.roll('1d2').total - 1]

def rollGold(character):
    character['GP'] = d20.roll('3d6').total * 10

def fillPdfAndOutput(character, postfix):
    template_pdf = pdfrw.PdfReader(csTemplate)
    ANNOT_KEY = '/Annots'
    ANNOT_FIELD_KEY = '/T'
    ANNOT_VAL_KEY = '/V'
    ANNOT_RECT_KEY = '/Rect'
    SUBTYPE_KEY = '/Subtype'
    WIDGET_SUBTYPE_KEY = '/Widget'
    for page in template_pdf.pages:
        annotations = page[ANNOT_KEY]
        for annotation in annotations:
            if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                if annotation[ANNOT_FIELD_KEY]:
                    key = annotation[ANNOT_FIELD_KEY][1:-1]
                    #print(key)
                    if key in character.keys():
                        if type(character[key]) == bool:
                            if character[key] == True:
                                annotation.update(pdfrw.PdfDict(AS=pdfrw.PdfName('Yes')))
                        else:
                            annotation.update(pdfrw.PdfDict(V='{}'.format(character[key])))
                            annotation.update(pdfrw.PdfDict(AP=''))
    
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))

    csOutput = 'cs' + str(postfix) + '.pdf'

    pdfrw.PdfWriter().write(csOutput, template_pdf)

    return csOutput

def saveCharacterAsTextFile(output_dir, character, postfix):
    env = Environment(loader=FileSystemLoader(searchpath='./'))
    template = env.get_template('text_template.jin')
    output_from_parsed_template = template.render(d=character)

# to save the results
    with open(os.path.join(output_dir, f'cs_{postfix}.txt'), 'w') as f:
        f.write(output_from_parsed_template)

def createAndSaveCharacter(output_dir, postfix):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    character = {}
    baseStats(character)
    chooseClass(character)
    chooseStats(character)
    noteMods(character)
    noteSavingThrows(character)
    rollHp(character)
    chooseAlignment(character)
    rollGold(character)
    chooseArmor(character)
    chooseWeapon(character)
    determineAttack(character)

    saveCharacterAsTextFile(output_dir, character, postfix)

def main():
    parser = argparse.ArgumentParser(description='Create some OSE characters.')
    parser.add_argument('character_count', metavar='Character Count', type=int, nargs=1,
                        help='The number of characters to create')

    args = parser.parse_args()

    for i in range(args.character_count[0]):
        createAndSaveCharacter('output', f'{i+1:03}')

if __name__ == '__main__':
    main()
