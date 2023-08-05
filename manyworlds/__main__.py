# __main__.py
import argparse
import manyworlds as mw
from termcolor import colored

def main():
    parser = argparse.ArgumentParser(prog="manyworlds")
    parser.add_argument('--input', help="input scenario file")
    parser.add_argument('--output', help="output file (either flat scenario file or mermaid file)")
    parser.add_argument('--mode', choices=['strict', 'relaxed'], default='strict', help='strict: one scenario per node, relaxed: one scenario per leaf node')
    parser.add_argument('--comments', default=False, action='store_true', help='output comments')
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