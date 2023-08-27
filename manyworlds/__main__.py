# __main__.py
import argparse
import manyworlds as mw
from termcolor import colored  # type: ignore


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


def print_scenario_forest(forest):
    """print scenario forest outline to terminal"""
    for sc in forest.scenarios():
        scenario_string = sc.name

        # Indentation:
        level: int = sc.level()
        if level > 1:
            scenario_string = (
                "   " * (level - 2) + colored("└─ ", "blue") + scenario_string
            )

        # Colon for organizational scenarios:
        if sc.is_organizational():
            scenario_string += ":"

        print(scenario_string)


if __name__ == "__main__":
    main()
