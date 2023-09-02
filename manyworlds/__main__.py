# __main__.py

from typing import Optional, Dict
import argparse

import manyworlds as mw


def main():
    parser = argparse.ArgumentParser(prog="manyworlds")
    parser.add_argument("--input", "-i", help="input scenario file")
    parser.add_argument("--output", "-o", help="output scenario file")
    parser.add_argument(
        "--mode",
        "-m",
        choices=["strict", "relaxed"],
        default="strict",
        help="flattening mode",
    )
    parser.add_argument(
        "--comments", "-c", default=False, action="store_true", help="output comments"
    )
    args = parser.parse_args()

    # read hierarchical feature file:
    forest = mw.ScenarioForest.from_file(args.input)

    print_scenario_forest(forest)

    # write flat feature file:
    if args.output:
        forest.flatten(args.output, mode=args.mode, comments=args.comments)


def print_scenario_forest(forest: mw.ScenarioForest) -> None:
    """print scenario forest outline to terminal"""
    level_open: Dict[int, bool] = {}
    for sc in forest.scenarios():
        scenario_string = sc.name

        # Indentation and branch shapes:
        level: int = sc.level()
        if level is None:
            continue
        if level > 1:

            # indentation:
            indentation: str = ""
            for lvl in range(2, level):
                indentation += (
                    "│   "
                    if (lvl in level_open.keys() and level_open[lvl])
                    else
                    "    "
                )

            # branch shape:
            branch_shape: str
            later_sibling: Optional[mw.scenario.Scenario] = next((
                sib
                for sib in sc.siblings()
                if sib.index() > sc.index()
            ), None)
            if later_sibling is not None:
                branch_shape = "├──"
                level_open[level] = True
            else:
                branch_shape = "└──"
                level_open[level] = False

            scenario_string = (
                indentation + branch_shape + " " + scenario_string
            )

        # Colon for organizational scenarios:
        if sc.is_organizational():
            scenario_string += ":"

        print(scenario_string)


if __name__ == "__main__":
    main()
