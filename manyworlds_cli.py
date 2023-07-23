import argparse
import manyworlds as mw

parser = argparse.ArgumentParser(prog="manyworld.py")
parser.add_argument('action', choices=['flatten', 'graph'], help="'flatten' to output flat scenario file, 'graph' to output mermaid file")
parser.add_argument('--input', help="input scenario file")
parser.add_argument('--output', help="output file (either flat scenario file or mermaid file)")
parser.add_argument('--mode', choices=['strict', 'relaxed'], default='strict')
parser.add_argument('--comments', choices=['on', 'off'], default='off')
args = parser.parse_args()

tree = mw.ScenarioForest.from_file(args.input)

# print tree:
for v in tree.graph.vs():
    level = tree.graph.neighborhood_size(v, mode="IN", order=100)
    indentation_string = ''
    if level > 1:
        indentation_string = '   '*(level-2) + '└─ '
    print(indentation_string + v['name'])

if args.action == 'flatten':
    tree.flatten(args.output, mode=args.mode, comments=args.comments)
elif args.action == 'graph':
    tree.graph_mermaid(args.output)