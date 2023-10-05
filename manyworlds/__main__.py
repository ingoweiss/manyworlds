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
        "--write-comments",
        "-c",
        default=False,
        action="store_true",
        help="output comments",
    )
    args = parser.parse_args()

    # read hierarchical feature file:
    feature = mw.Feature.from_file(args.input)

    print_feature_outline(feature)

    # write flat feature file:
    if args.output:
        feature.flatten(args.output, mode=args.mode, write_comments=args.write_comments)


def print_feature_outline(feature: mw.Feature) -> None:
    """print feature outline to terminal"""
    level_open: Dict[int, bool] = {}
    branch_shape: str
    later_sibling: bool
    sib: mw.scenario.Scenario
    sib_index: Optional[int]

    for sc in feature.scenarios():
        scenario_string = sc.name

        # Indentation and branch shapes:
        level: Optional[int] = sc.level()
        index: Optional[int] = sc.index()
        if level is None or index is None:
            continue
        if level > 1:
            # indentation:
            indentation: str = ""
            for lvl in range(2, level):
                indentation += (
                    "│   " if (lvl in level_open.keys() and level_open[lvl]) else "    "
                )

            # branch shape:
            later_sibling = False
            for sib in sc.siblings():
                sib_index = sib.index()
                if sib_index is None:
                    continue
                if sib_index > index:
                    later_sibling = True

            if later_sibling is True:
                branch_shape = "├──"
                level_open[level] = True
            else:
                branch_shape = "└──"
                level_open[level] = False

            scenario_string = indentation + branch_shape + " " + scenario_string

        # Colon for organizational scenarios:
        if sc.is_organizational():
            scenario_string += ":"

        print(scenario_string)


if __name__ == "__main__":
    main()
