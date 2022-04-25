# main.py

import argparse
import logging
import os

from jinja2 import Environment, FileSystemLoader

from character_builder import CharacterBuilder


def saveCharacterAsTextFile(output_dir, character, postfix):
    env = Environment(loader=FileSystemLoader(searchpath='./'))
    template = env.get_template('text_template.jin')
    output_from_parsed_template = template.render(d=character)

    with open(os.path.join(output_dir, f'cs_{postfix}.txt'), 'w') as f:
        f.write(output_from_parsed_template)

def createAndSaveCharacter(builder, output_dir, postfix):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    character = builder.build_char()

    saveCharacterAsTextFile(output_dir, character, postfix)

def main():
    parser = argparse.ArgumentParser(description='Create some OSE characters.')
    parser.add_argument('character_count', metavar='Character Count', type=int, nargs=1,
                        help='The number of characters to create')

    args = parser.parse_args()

    builder = CharacterBuilder()

    for i in range(args.character_count[0]):
        createAndSaveCharacter(builder, 'output', f'{i+1:03}')

if __name__ == '__main__':
    main()