# __main__.py
import argparse
import manyworlds as mw
from termcolor import colored

def main():
    parser = argparse.ArgumentParser(prog="manyworlds")
    parser.add_argument('--input', '-i',
                        help="input scenario file")
    parser.add_argument('--output', '-o',
                        help="output scenario file")
    parser.add_argument('--mode', '-m',
                        choices=['strict', 'relaxed'],
                        default='strict',
                        help='flattening mode')
    parser.add_argument('--comments', '-c',
                        default=False,
                        action='store_true',
                        help='output comments')
    args = parser.parse_args()

    tree = mw.ScenarioForest.from_file(args.input)

    # print tree:
    for sc in tree.scenarios():
        level = sc.level()
        if level > 1:
            indentation_string = '   '*(level-2) + colored('└─ ', 'blue')
        else:
            indentation_string = ''
        print(indentation_string + sc.name)

    tree.flatten(args.output, mode=args.mode, comments=args.comments)

if __name__ == "__main__":
    main()