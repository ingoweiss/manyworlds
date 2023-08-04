import argparse
from src.manyworlds.scenario_forest import ScenarioForest
from termcolor import colored

parser = argparse.ArgumentParser(prog="manyworld.py")
parser.add_argument('action', choices=['flatten', 'graph'], help="'flatten' to output flat scenario file, 'graph' to output mermaid file")
parser.add_argument('--input', help="input scenario file")
parser.add_argument('--output', help="output file (either flat scenario file or mermaid file)")
parser.add_argument('--mode', choices=['strict', 'relaxed'], default='strict')
parser.add_argument('--comments', choices=['on', 'off'], default='off')
args = parser.parse_args()

tree = ScenarioForest.from_file(args.input)

# print tree:
for sc in tree.scenarios():
    level = sc.level()
    if level > 1:
        indentation_string = '   '*(level-2) + colored('└─ ', 'blue')
    else:
        indentation_string = ''
    print(indentation_string + sc.name)

if args.action == 'flatten':
    tree.flatten(args.output, mode=args.mode, comments=args.comments)
elif args.action == 'graph':
    tree.graph_mermaid(args.output)