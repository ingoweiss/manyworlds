import argparse
from manyworlds.scenario_tree import ScenarioTree

parser = argparse.ArgumentParser(prog="manyworld.py")
parser.add_argument('action', choices=['flatten', 'graph'], help="'flatten' to output flat scenario file, 'graph' to output mermaid file")
parser.add_argument('--input', help="input scenario file")
parser.add_argument('--output', help="output file (either flat scenario file or mermaid file)")
parser.add_argument('--relaxed', action='store_true', help="allow multipe 'When/Then' groups in one scenario")
args = parser.parse_args()

tree = ScenarioTree(args.input)

strict = not args.relaxed

if args.action == 'flatten':
    tree.flatten(args.output, strict=strict)
elif args.action == 'graph':
    tree.graph(args.output)