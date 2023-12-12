"""
Autobot event lists.
"""

import argparse
from datetime import datetime
import dotsi  # type: ignore
import json
import logging
import logging.handlers
import os
import time

from app_settings import load, week_days
import events_parser

# Get application logger.
log = logging.getLogger(__name__)

# Load application settings.
settings = dotsi.Dict(load("./settings.yaml"))

def main(ePath, dMap):

    # Load application settings.
    settings = dotsi.Dict(load("./settings.yaml"))

    # Initialise app name and version from settings.
    app_name = settings.app.APP_NAME
    app_version = settings.app.APP_VERSION

    # Create logger. Use rotating log files.
    log.setLevel(settings.log.DEF_LEVEL)
    handler = logging.handlers.RotatingFileHandler(app_name + ".log", maxBytes=settings.log.MAX_SIZE, backupCount=settings.log.MAX_FILES)
    handler.setFormatter(logging.Formatter(fmt=f"%(asctime)s.%(msecs)03d [{app_name}] [%(levelname)-8s] %(message)s", datefmt="%Y%m%d-%H:%M:%S", style="%"))
    logging.Formatter.converter = time.localtime
    log.addHandler(handler)

    log.info(f"Initialising application: {app_name}, version: {app_version}")
    log.info(f"Events path: {ePath}")
    log.info(f"Device map: {dMap}")

    # Traverse event directory structure looking for event files.
    event_parser = events_parser.Events_parser(log, ePath, dMap)
    event_parser.traverse_path()

    # Get all the event data totals.
    print(f"Total number of events: {event_parser.event_data.total_events}")

    # Get data by day.
    for day in week_days:
        print(f"Events for {day}")
        for ev in event_parser.event_data.all_events:
            if ev.day == day:
                print(f"   {ev.event_type}")


if __name__ == "__main__":

    # Get program arguments.
    parser = argparse.ArgumentParser(description="Autobot events scraper.")
    parser.add_argument("-d", "--dir", help="Autobot events directory.")
    parser.add_argument("-m", "--map", help="Device mapping file.")
    parser.add_argument("-v", "--version", help="Program version.", action="store_true")
    args = parser.parse_args()

    # Defaults.
    ePath = os.getcwd()

    if args.version:
        print(f"Program version : {settings.app.APP_VERSION}")
    else:
        # Need to have root director to parse,
        # And a device mapping file.
        if args.dir:
            ePath = args.dir
        if args.map:
            dMap = args.map
            main(ePath, dMap)
