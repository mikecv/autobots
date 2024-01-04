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

def main(ePath, dMap, cntrl, day):

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
    log.info(f"Reporting event exceptions: {settings.report.EXCEPTIONS}")

    # Traverse event directory structure looking for event files.
    event_parser = events_parser.Events_parser(log, ePath, dMap)
    event_parser.traverse_path()

    # Get data by controller ID (for all days).
    if (cntrl is not None) and (day is None):
        reports.report_by_device(settings, event_parser, cntrl)

    # Get data by controller for a specific day.
    if (cntrl is not None) and (day is not None):
        reports.report_by_device_on_day(settings, event_parser, cntrl, day)

    # Get data for all controllers on a specific day.
    if (cntrl is None) and (day is not None):
        for dev in list(event_parser.dev_map.values()):
            reports.report_by_device(settings, event_parser, dev)
    

if __name__ == "__main__":

    # Get program arguments.
    parser = argparse.ArgumentParser(description="Autobot events scraper.")
    parser.add_argument("-p", "--path", help="Autobot events path.")
    parser.add_argument("-m", "--map", help="Device mapping file.")
    parser.add_argument("-c", "--cntrl", help="Report for a controller ID.")
    parser.add_argument("-d", "--day", help="Report for a particular day.")
    parser.add_argument("-v", "--version", help="Program version.", action="store_true")
    args = parser.parse_args()

    # Defaults.
    ePath = os.getcwd()
    cntrl = None
    day = None

    if args.version:
        print(f"Program version : {settings.app.APP_VERSION}")
    else:
        # Need to have root director to parse,
        # And a device mapping file.
        if args.path:
            ePath = args.path
        if args.map:
            dMap = args.map
        else:
            print("Require a device mapping file, \"-m option\".")
        if args.cntrl:
            cntrl = args.cntrl
        if args.day:
            day = args.day
        main(ePath, dMap, cntrl, day)

    """
    Example usage for case of report by device ID (11027).

    Report for a specific controller for all days.
    $ python3 autobots_app.py -p ./data/Test/ -m ./device_map.json -c 11027
    
    Report for a specific controller for a specific day.
    $ python3 autobots_app.py -p ./data/Test/ -m ./device_map.json -c 11027 -d Monday
    """
    