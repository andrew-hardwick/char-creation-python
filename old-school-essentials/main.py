# main.py

import os

import d20
import pdfrw

from PyPDF2 import PdfFileMerger


csTemplate = 'template.pdf'
csOutput = 'characterSheet.pdf'

statRoll = '3d6'
classOptions = ['cleric', 'dwarf', 'elf', 'fighter', 'halfling', 'magic user', 'thief']
classReqs = {'dwarf': {'CON': 9}, 'elf': {'INT': 9}, 'halfling': {'CON': 9, 'DEX': 9}}
standardBonus = { 3 : -3, 4 : -2, 5 : -2, 6 : -1, 7 : -1, 8 : -1, 9 : 0, 10 : 0, 11 : 0, 12 : 0, 13 : 1, 14 : 1, 15 : 1, 16 : 2, 17 : 2, 18 : 3 }
alternativeBonus = { 3 : -2, 4 : -1, 5 : -1, 6 : -1, 7 : -1, 8 : -1, 9 : 0, 10 : 0, 11 : 0, 12 : 0, 13 : 1, 14 : 1, 15 : 1, 16 : 1, 17 : 1, 18 : 2 }
strOpenDoors = { 3 : 1, 4 : 1, 5 : 1, 6 : 1, 7 : 1, 8 : 1, 9 : 2, 10 : 2, 11 : 2, 12 : 2, 13 : 3, 14 : 3, 15 : 3, 16 : 4, 17 : 4, 18 : 5}
intLanguages = { 3 : 'broken speech', 4 : 'Native', 5 : 'Native', 6 : 'Native', 7 : 'Native', 8 : 'Native', 9 : 'Native', 10 : 'Native', 11 : 'Native', 12 : 'Native', 13 : 'Native + 1 Additional', 14 : 'Native + 1 Additional', 15 : 'Native + 1 Additional', 16 : 'Native + 2 Additional', 17 : 'Native + 2 Additional', 18 : 'Native + 3 Additional' }
intLiteracy = { 3 : False, 4 : False, 5 : False, 6 : True, 7 : True, 8 : True, 9 : True, 10 : True, 11 : True, 12 : True, 13 : True, 14 : True, 15 : True, 16 : True, 17 : True, 18 : True }
savingThrows = { 'cleric' : [ 11, 12, 14, 16, 15 ], 'dwarf' : [ 8, 9, 10, 13, 12 ], 'elf' : [ 12, 13, 13, 15, 15 ], 'fighter' : [ 12, 13, 14, 15, 16 ], 'halfling' : [ 8, 9, 10, 13, 12 ], 'magic user' : [ 13, 14, 13, 16, 15 ], 'thief' : [ 13, 14, 13, 16, 15 ], }
classHd = { 'cleric' : '1d6', 'dwarf' : '1d8', 'elf' : '1d6', 'fighter' : '1d8', 'halfling' : '1d6', 'magic user' : '1d4', 'thief' : '1d4', }
alignmentOptions = ['Lawful', 'Neutral']
classArmorOptions = { 'cleric' : [ 'Unarmoured', 'Leather', 'Chainmail' ], 'dwarf' : [ 'Unarmoured', 'Leather', 'Chainmail' ], 'elf' : [ 'Unarmoured', 'Leather', 'Chainmail' ], 'fighter' : [ 'Unarmoured', 'Leather', 'Chainmail' ], 'halfling' : [ 'Unarmoured', 'Leather', 'Chainmail' ], 'magic user' : [ 'Unarmoured' ], 'thief' : [ 'Unarmoured', 'Leather' ] }
classShield = { 'cleric' : True, 'dwarf' : True, 'elf' : True, 'fighter' : True, 'halfling' : True, 'magic user' : False, 'thief' : False }
armorclass = { 'Unarmoured': 9, 'Leather' : 7, 'Chainmail' : 5 }
armorBaseMove = { 'Unarmoured': 120, 'Leather' : 90, 'Chainmail' : 60 }
classListen = { 'cleric' : 1, 'dwarf' : 2, 'elf' : 2, 'fighter' : 1, 'halfling' : 2, 'magic user' : 1, 'thief' : 1 }
classSecretDoor = { 'cleric' : 1, 'dwarf' : 1, 'elf' : 2, 'fighter' : 1, 'halfling' : 1, 'magic user' : 1, 'thief' : 1 }
classRoomTrap = { 'cleric' : 1, 'dwarf' : 2, 'elf' : 1, 'fighter' : 1, 'halfling' : 1, 'magic user' : 1, 'thief' : 1 }
classXpToLevel = { 'cleric' : 1500, 'dwarf' : 2200, 'elf' : 4000, 'fighter' : 2000, 'halfling' : 2000, 'magic user' : 2500, 'thief' : 1200 }

def baseStats(character):
    character['Level'] = 1
    character['Equipment'] = 'Backpack\nLantern\nFlask of Oil (5)\nJug of Ale (1)\nRations (7 days)\nLarge Sack\nWaterskin'
    character['XP'] = 0

def chooseClass(character):
    character['Character Class'] = classOptions[d20.roll('d7').total - 1]
    character['Listen at Door'] = classListen[character['Character Class']]
    character['Find Secret Door'] = classSecretDoor[character['Character Class']]
    character['Find Room Trap'] = classRoomTrap[character['Character Class']]
    character['XP for Next Level'] = classXpToLevel[character['Character Class']]

def chooseArmor(character):
    availableArmor = classArmorOptions[character['Character Class']]

    roll = '1d' + str(len(availableArmor))

    character['armor'] = availableArmor[d20.roll(roll).total - 1]

    character['Weapons and Armour'] = character['armor'] + '\n'
    character['AC'] = armorclass[character['armor']] + character['DEX AC Mod']
    
    if classShield[character['Character Class']]:
        if d20.roll('1d2').total == 1:
            character['Weapons and Armour'] += 'Shield\n'
            character['AC'] = character['AC'] - 1

    character['Exporation Movement'] = armorBaseMove[character['armor']]
    character['Overland Movement'] = int(armorBaseMove[character['armor']] / 5)
    character['Encounter Movement'] = int(armorBaseMove[character['armor']] / 3)

def statsValidForClass(character):
    if character['Character Class'] not in classReqs.keys():
        return True
    else:
        reqs = classReqs[character['Character Class']]

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
    character['STR Melee Mod'] = standardBonus[character['STR']]
    character['Open Stuck Door'] = strOpenDoors[character['STR']]
    character['Languages'] = intLanguages[character['INT']]
    character['Literacy'] = intLiteracy[character['INT']]
    character['DEX AC Mod'] = -standardBonus[character['DEX']]
    character['Unarmoured AC'] = 9 + character['DEX AC Mod']
    character['Dex Missile Mod'] = standardBonus[character['DEX']]
    character['Initiative DEX Mod'] = alternativeBonus[character['DEX']]
    character['Reactions CHA Mod'] = alternativeBonus[character['CHA']]
    character['Magic Save Mod'] = standardBonus[character['WIS']]
    character['CON HP Mod'] = standardBonus[character['CON']]

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
    character['savingThrows'] = savingThrows[character['Character Class']]
    character['Death Save'] = character['savingThrows'][0]
    character['Wands Save'] = character['savingThrows'][1]
    character['Paralysis Save'] = character['savingThrows'][2]
    character['Breath Save'] = character['savingThrows'][3]
    character['Spells Save'] = character['savingThrows'][4]

def rollHp(character):
    character['Max HP'] = d20.roll(classHd[character['Character Class']]).total + character['CON HP Mod']

    if character['Max HP'] < 1:
        character['Max HP'] = 1

    character['HP'] = character['Max HP']

def chooseAlignment(character):
    character['Alignment'] = alignmentOptions[d20.roll('1d2').total - 1]

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