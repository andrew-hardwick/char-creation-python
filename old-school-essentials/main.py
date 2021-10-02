# main.py

import os

import d20
import pdfrw

from PyPDF2 import PdfFileMerger

from constants import *


csTemplate = 'template.pdf'
csOutput = 'characterSheet.pdf'

statRoll = '3d6'

def baseStats(character):
    character['Level'] = 1
    character['Equipment'] = 'Backpack\nLantern\nFlask of Oil (5)\nJug of Ale (1)\nRations (7 days)\nLarge Sack\nWaterskin'
    character['XP'] = 0

def chooseClass(character):
    character['class'] = CLASS_OPTIONS[d20.roll('d7').total - 1]
    character['Listen at Door'] = CLASS_LISTEN[character['class']]
    character['Find Secret Door'] = CLASS_SECRET_DOOR[character['class']]
    character['Find Room Trap'] = CLASS_ROOM_TRAP[character['class']]
    character['XP for Next Level'] = CLASS_XP_TO_LEVEL[character['class']]
    character['Character Class'] = CLASS_DISPLAY[character['class']]

def chooseArmor(character):
    availableArmor = CLASS_ARMOR_OPTIONS[character['class']]

    roll = '1d' + str(len(availableArmor))

    character['armor'] = availableArmor[d20.roll(roll).total - 1]

    character['Weapons and Armour'] = character['armor'] + '\n'
    character['AC'] = ARMOR_CLASS[character['armor']] + character['DEX AC Mod']
    
    character['hasShield'] = False

    if CLASS_SHIELD[character['class']]:
        if d20.roll('1d2').total == 1:
            character['Weapons and Armour'] += 'Shield\n'
            character['AC'] = character['AC'] - 1
            character['hasShield'] = True

    character['Exporation Movement'] = ARMOR_BASE_MOVE[character['armor']]
    character['Overland Movement'] = int(ARMOR_BASE_MOVE[character['armor']] / 5)
    character['Encounter Movement'] = int(ARMOR_BASE_MOVE[character['armor']] / 3)

def chooseWeapon(character):
    availableWeapons = CLASS_WEAPONS[character['class']][character['hasShield']]

    selected = availableWeapons[d20.roll('1d' + str(len(availableWeapons))).total - 1]

    character['Weapons and Armour'] += selected + ' (' + WEAPON_DAMAGE[selected] + ')\n'

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
    character['STR Melee Mod'] = STANDARD_BONUS[character['STR']]
    character['Open Stuck Door'] = STR_OPEN_DOORS[character['STR']]
    character['Languages'] = INT_LANGUAGES[character['INT']]
    character['Literacy'] = INT_LITERACY[character['INT']]
    character['DEX AC Mod'] = -STANDARD_BONUS[character['DEX']]
    character['Unarmoured AC'] = 9 + character['DEX AC Mod']
    character['Dex Missile Mod'] = STANDARD_BONUS[character['DEX']]
    character['Initiative DEX Mod'] = ALTERNATIVE_BONUS[character['DEX']]
    character['Reactions CHA Mod'] = ALTERNATIVE_BONUS[character['CHA']]
    character['Magic Save Mod'] = STANDARD_BONUS[character['WIS']]
    character['CON HP Mod'] = STANDARD_BONUS[character['CON']]

def determineAttack(character):
    character['THAC0'] = 19
    character['THAC1'] = 18
    character['THAC2'] = 17
    character['THAC3'] = 16
    character['THAC4'] = 15
    character['THAC5'] = 14
    character['THAC6'] = 13
    character['THAC7'] = 12
    character['THAC8'] = 11
    character['THAC9'] = 10

def noteSavingThrows(character):
    character['SAVING_THROWS'] = SAVING_THROWS[character['class']]
    character['Death Save'] = character['SAVING_THROWS'][0]
    character['Wands Save'] = character['SAVING_THROWS'][1]
    character['Paralysis Save'] = character['SAVING_THROWS'][2]
    character['Breath Save'] = character['SAVING_THROWS'][3]
    character['Spells Save'] = character['SAVING_THROWS'][4]

def rollHp(character):
    character['Max HP'] = d20.roll(CLASS_HD[character['class']]).total + character['CON HP Mod']

    if character['Max HP'] < 1:
        character['Max HP'] = 1

    character['HP'] = character['Max HP']

def chooseAlignment(character):
    character['Alignment'] = ALIGNMENT_OPTIONS[d20.roll('1d2').total - 1]

def rollGold(character):
    character['GP'] = d20.roll('3d6').total

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

def createAndSaveCharacter(postfix):
    character = {}
    baseStats(character)
    chooseClass(character)
    chooseStats(character)
    noteMods(character)
    determineAttack(character)
    noteSavingThrows(character)
    rollHp(character)
    chooseAlignment(character)
    rollGold(character)
    chooseArmor(character)
    chooseWeapon(character)

    return fillPdfAndOutput(character, postfix)

def main():
    files = []
    for i in range(10):
        files.append(createAndSaveCharacter(i))

    merger = PdfFileMerger()

    for file in files:
        merger.append(file)

    merger.write('characters.pdf')
    merger.close()

    for file in files:
        os.remove(file)

main()