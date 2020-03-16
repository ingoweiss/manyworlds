import argparse
from manyworlds import scenario_tree as mw
import pdb

parser = argparse.ArgumentParser(prog="manyworld.py")
parser.add_argument('action', choices=['flatten', 'graph'])
parser.add_argument('--input')
parser.add_argument('--output')
parser.add_argument('--strict', action='store_true')
args = parser.parse_args()

tree = mw.ScenarioTree(args.input)

if args.action == 'flatten':
    tree.flatten(args.output, strict=args.strict)
elif args.action == 'graph':
    tree.graph(args.output)