"""
Autobot event lists.
Aligned with format of event files for Autobot script.
"""

import argparse
from datetime import datetime
import dotsi  # type: ignore
import logging
import logging.handlers
import os
import time

from app_settings import load, week_days
import events_parser
import reports

# Get application logger.
log = logging.getLogger(__name__)

# Load application settings.
settings = dotsi.Dict(load("./settings.yaml"))

def main(ePath, dMap, cntrl):

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
    log.info(f"Report for controller: {cntrl}")

    # Traverse event directory structure looking for event files.
    event_parser = events_parser.Events_parser(log, ePath, dMap)
    event_parser.traverse_path()

    # # Get data by day.
    # for day in week_days:
    #     print("="*80)
    #     print(f"Events for {day}")
    #     print("="*80)
    #     for ev in event_parser.event_data.all_events:
    #         if ev.day == day:
    #             print(f"   {ev.time} : {ev.event_type:20} : {ev.params}")
    # print("="*80)

    # Get data by controller ID.
    if cntrl is not None:
        reports.report_by_device(event_parser, cntrl)
    # for cntrl in event_parser.dev_map:
    #     reports.report_by_device(event_parser, event_parser.dev_map[cntrl])


if __name__ == "__main__":

    # Get program arguments.
    parser = argparse.ArgumentParser(description="Autobot events scraper.")
    parser.add_argument("-d", "--dir", help="Autobot events directory.")
    parser.add_argument("-m", "--map", help="Device mapping file.")
    parser.add_argument("-c", "--cntrl", help="Report for a controller ID.")
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
        else:
            print("Require a device mapping file, \"-m option\".")
        if args.cntrl:
            cntrl = args.cntrl
            main(ePath, dMap, cntrl)
