#
# Created by Renatus Madrigal on 02/14/2025
#

from argparse import ArgumentParser
from pyrealrunner.cli import main as cli_main
from pyrealrunner.gui import main as gui_main
import sys
import asyncio


def main():
    parser = ArgumentParser(
        prog="PyRealRunner",
        usage="%(prog)s [options]",
        description="A fake runner implemented by python for iOS"
    )
    parser.add_argument(
        "--gui",
        "-g",
        action="store_true",
        help="Use GUI interface",
    )
    parser.add_argument(
        "--config",
        help="The path to config.json"
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List all connected device"
    )
    args = parser.parse_args()
    if args.gui:
        gui_main(args)
    else:
        cli_main(args)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        sys.exit(1)
