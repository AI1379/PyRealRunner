#
# Created by Renatus Madrigal on 02/14/2025
#

from argparse import ArgumentParser
from .run import run
from .route import Route
from .device import DeviceManager, Device
from .util import run_in_thread, EventBridge, loop_set_debug
from typing import Coroutine
from concurrent.futures import Future
import os
import sys
import json
import asyncio
import signal
import threading


def extract_config(config_arg: str) -> dict:
    config_path = config_arg
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        for key in config["path"]:
            key["lng"] = float(key["lng"])
            key["lat"] = float(key["lat"])
    return config


def exec(config_arg: str):
    config = extract_config(config_arg)
    v: float = config["speed"]
    dt: float = config["interval"]
    loop_cnt: int = config["loop_count"]
    udid: str = config["udid"]
    dev = Device(udid)
    route = Route(config["path"])

    print(f"Running with config: {config}")
    loop_set_debug(asyncio.get_event_loop())
    try:
        dev.start_tunnel()
        print("Running main coroutine")
        asyncio.run(run(route, dev, loop_cnt, v, dt))
    except Exception as ex:
        print(f"Exception caught in main coroutine: {ex}")
        raise
    finally:
        asyncio.get_event_loop().stop()


def main(args):
    if args.list_devices:
        print(DeviceManager.get_devices_info())
    else:
        config = args.config if args.config else "./config.json"
        loop_set_debug(asyncio.get_event_loop())
        asyncio.run(exec(config))


if __name__ == '__main__':
    parser = ArgumentParser(
        prog="PyRealRunner",
        usage="%(prog)s [options]",
        description="A fake runner implemented by python for iOS"
    )
    parser.add_argument(
        "--config",
        help="The path to config.json",
        type=str
    )
    parser.add_argument(
        "--list-devices",
        help="List all connected device"
    )
    parser.add_argument(
        "-h",
        "--help",
        help="Show help message"
    )
    args = parser.parse_args()
    if args.help:
        parser.print_help()
    else:
        main(args)
