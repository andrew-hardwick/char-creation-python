# character_builder.py

import json
import logging
import os

import d20


class CharacterBuilder():
	def __init__(self):
		with open('tables.json', 'r') as f:
			self._data_tables = json.loads(f.read())

		with open('occupations.json', 'r') as f:
			self._occupations = json.loads(f.read())

		with open('equipment_packs.json', 'r') as f:
			self._equipment_packs = json.loads(f.read())

		with open('prime_requisite_bonus.json', 'r') as f:
			self._prime_requisite_stats = json.loads(f.read())

		self._stat_roll = '3d6'
		self._gold_roll = '3d6*10'

	def build_char(self):
		character = {}

		self.select_base_stats(character)
		self.select_class(character)
		self.roll_valid_stats(character)
		self.note_prime_requisites(character)
		self.note_mods(character)
		self.note_saving_throws(character)
		self.roll_hp(character)
		self.choose_alignment(character)
		self.roll_gold(character)
		self.choose_armor(character)
		self.choose_occupation(character)
		self.determine_attack(character)
		self.choose_equipment(character)

		return character

	def select_base_stats(self, character):
		character['Level'] = 1
		character['XP'] = 0
		character['weapons_and_armor'] = ''

	def select_class(self, character):
		character['class'] = self._data_tables['CLASS_OPTIONS'][d20.roll('d7').total - 1]
		character['listen_doors'] = self._data_tables['CLASS_LISTEN'][character['class']]
		character['find_secret_doors'] = self._data_tables['CLASS_SECRET_DOOR'][character['class']]
		character['find_room_trap'] = self._data_tables['CLASS_ROOM_TRAP'][character['class']]
		character['xp_to_level'] = self._data_tables['CLASS_XP_TO_LEVEL'][character['class']]
		character['display_class'] = self._data_tables['CLASS_DISPLAY'][character['class']]

	def roll_valid_stats(self, character):
		self.roll_stats(character)

		while not self.is_stats_valid_for_class(character):
			self.roll_stats(character)

	def roll_stats(self, character):
		character['STR'] = d20.roll(self._stat_roll).total
		character['INT'] = d20.roll(self._stat_roll).total
		character['DEX'] = d20.roll(self._stat_roll).total
		character['WIS'] = d20.roll(self._stat_roll).total
		character['CON'] = d20.roll(self._stat_roll).total
		character['CHA'] = d20.roll(self._stat_roll).total

	def is_stats_valid_for_class(self, character):
		if character['class'] not in self._data_tables['CLASS_REQS'].keys():
			return True
		else:
			stat_requirements = self._data_tables['CLASS_REQS'][character['class']]

			result = True

			for stat in stat_requirements.keys():
				result = result & (character[stat] >= stat_requirements[stat])

			return result

	def note_prime_requisites(self, character):
		prime_req_option = self._prime_requisite_stats[character['class']]

		if prime_req_option['simple'] == 'yes':
			character['bonus_xp'] = self._data_tables['STANDARD_PRIME_REQUISITE'][str(character[prime_req_option['stat']])]
		else:
			valid_cases = [case['bonus'] for case in prime_req_option['cases'] if self.is_prime_req_case_met(case['stats'], character)]

			if len(valid_cases) > 0:
				character['bonus_xp'] = max(valid_cases)
			else:
				character['bonus_xp'] = "+0"

	def is_prime_req_case_met(self, stats, character):
		for stat in stats:
			if character[stat] < stats[stat]:
				return False
		return True

	def note_mods(self, character):
		character['str_melee_mod'] = self._data_tables['STANDARD_BONUS'][str(character['STR'])]
		character['open_doors'] = self._data_tables['STR_OPEN_DOORS'][str(character['STR'])]
		character['Languages'] = self._data_tables['INT_LANGUAGES'][str(character['INT'])]
		character['Literacy'] = self._data_tables['INT_LITERACY'][str(character['INT'])]
		character['dex_ac_mod'] = self._data_tables['STANDARD_BONUS'][str(character['DEX'])]
		character['Unarmoured AC'] = 9 - character['dex_ac_mod']
		character['dex_missile_mod'] = self._data_tables['STANDARD_BONUS'][str(character['DEX'])]
		character['initiative_mod'] = self._data_tables['ALTERNATIVE_BONUS'][str(character['DEX'])]
		character['reactions_cha_mod'] = self._data_tables['ALTERNATIVE_BONUS'][str(character['CHA'])]
		character['magic_save_mod'] = self._data_tables['STANDARD_BONUS'][str(character['WIS'])]
		character['con_hp_mod'] = self._data_tables['STANDARD_BONUS'][str(character['CON'])]

	def note_saving_throws(self, character):
		character['SAVING_THROWS'] = self._data_tables['SAVING_THROWS'][character['class']]
		character['Death_Save'] = character['SAVING_THROWS'][0]
		character['Wands_Save'] = character['SAVING_THROWS'][1]
		character['Paralysis_Save'] = character['SAVING_THROWS'][2]
		character['Breath_Save'] = character['SAVING_THROWS'][3]
		character['Spells_Save'] = character['SAVING_THROWS'][4]

	def roll_hp(self, character):
		character['HD'] = self._data_tables['CLASS_HD'][character['class']]
		character['Max HP'] = d20.roll(character['HD']).total + character['con_hp_mod']

		if character['Max HP'] < 1:
			character['Max HP'] = 1

		character['HP'] = character['Max HP']

	def choose_alignment(self, character):
		character['Alignment'] = self._data_tables['ALIGNMENT_OPTIONS'][d20.roll('1d2').total - 1]

	def roll_gold(self, character):
		character['GP'] = d20.roll(self._gold_roll).total

	def choose_armor(self, character):
		available_armor = self._data_tables['CLASS_ARMOR_OPTIONS'][character['class']]

		roll = '1d' + str(len(available_armor))

		character['armor'] = available_armor[d20.roll(roll).total - 1]

		if character['armor'] in self._data_tables['ARMOR_DISPLAY']:
			character['weapons_and_armor'] += self._data_tables['ARMOR_DISPLAY'][character['armor']] + '\n'

		character['AC'] = self._data_tables['ARMOR_CLASS'][character['armor']] - character['dex_ac_mod']

		character['hasShield'] = 'no'

		if self._data_tables['CLASS_SHIELD'][character['class']]:
			if d20.roll('1d2').total == 1:
				character['weapons_and_armor'] += 'Shield\n'
				character['AC'] = character['AC'] - 1
				character['hasShield'] = 'yes'

		character['exploration_speed'] = self._data_tables['ARMOR_BASE_MOVE'][character['armor']]
		character['overland_speed'] = int(character['exploration_speed'] / 5)
		character['encounter_speed'] = int(character['exploration_speed'] / 3)

	def choose_occupation(self, character):
		available_weapons = self._data_tables['CLASS_WEAPONS'][character['class']][character['hasShield']]

		available_occupations = [occupation for occupation in self._occupations if occupation['weapon_equiv'] in available_weapons]

		selected = available_occupations[d20.roll(f'1d{len(available_occupations)}').total - 1]

		character['occupation'] = selected['name']

		character['weapon'] = selected['weapon']
		character['weapon_equiv'] = selected['weapon_equiv']
		character['damage'] = self._data_tables['WEAPON_DAMAGE'][selected['weapon_equiv']]
		character['weapons_and_armor'] += selected['weapon'] + ' (' + character['damage'] + ')\n'

		character['GP'] = character['GP'] - self._data_tables['WEAPON_COST'][selected['weapon_equiv']]

		character['flavor_equipment'] = selected['items'] + '\n'

	def determine_attack(self, character):
		melee = self._data_tables['WEAPON_MELEE'][character['weapon_equiv']]

		bonus = character['str_melee_mod'] if melee else character['dex_missile_mod']

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

	def choose_equipment(self, character):
		available_kits = [pack for pack in self._equipment_packs if pack['cost'] <= character['GP']]

		selected = available_kits[d20.roll(f'1d{len(available_kits)}').total - 1]

		kit = '\n'.join(selected['item_list'])

		character['equipment'] = character['weapons_and_armor'] + character['flavor_equipment'] + kit
