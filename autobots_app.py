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
import re
import time

import app_settings

# Get application logger.
log = logging.getLogger(__name__)

# Load application settings.
settings = dotsi.Dict(app_settings.load("./settings.yaml"))

def main(ePath):

    # # Load application settings.
    # settings = dotsi.Dict(app_settings.load("./settings.yaml"))

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

    # Traverse event directory structure looking for event files.
    traverse_directory(ePath)

def process_json_file(file_path):

    # Get device mapping.
    dmap_file = './data/device_map.json'
    # Maps script devices to actual devices.
    dev_map = get_device_mapping(dmap_file)
    if dev_map is not None:
        # We have a device map, so parse for events.
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                # Process the json event data.
                log.info(f"Processing JSON file: {file_path}")
                # Get period for trip.
                trip_period = data['category']
                log.debug(f"Process period: {trip_period}")
                # Get the trip details.
                cntrl_id = data['_trip_info']['controller_id']
                log.debug(f"Controller Id: {cntrl_id}")
                cntrl_id = data['_trip_info']['controller_id']
                dev_id = dev_map[cntrl_id]
                log.debug(f"Mapped device Id: {dev_id}")
                # Process event data in the trip.
                for event in data['events']:
                    log.debug(f"Trip event string: {event}")
                    utime, event_type, event_params = parse_event(event)
                    event_day = datetime.utcfromtimestamp(utime).strftime('%A')
                    event_time = datetime.utcfromtimestamp(utime).strftime('%H:%M:%S')
                    log.debug(f"Found event at: {utime} : {event_day} - {event_time}")
                    log.debug(f"Found event: {event_type}")
                    log.debug(f"Event arguments: {event_params}")
            except json.JSONDecodeError as e:
                log.error(f"Error decoding JSON event file: {file_path}: {e}")
    else:
        log.error(f"Error decoding JSON device mapping file: {dmap_file}: {e}")


def get_device_mapping(dmap):
 
    # Open JSON device mapping file and create dictionary
    with open(dmap, 'r') as m_file:
        try:
            mmap = json.load(m_file)
            device_map = {}
            # Populate dictionary with device mappings.
            for device in mmap["controllers"]:
                device_map[device] = mmap["controllers"][device]["id"]
            log.debug(f"Device mapping file: {device_map}")
            return device_map
        except json.JSONDecodeError as e:
            log.error(f"Error decoding machine mapping file: {e}")
            return None

def traverse_directory(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                process_json_file(file_path)

def parse_event(event):
    # Search for events with parameters.
    event_pattern = re.compile(r'([0-9]{1,2}/[0-9]{2}/[0-9]{4}) ([0-9]{1,2}:[0-9]{2}:[0-9]{2}) .*?\,*?EVENT ([0-9]+) ([0-9]+) (.+)/(.+)/(.+)/([-0-9]+)/([0-9]+) (\w+) (.+) v:(.+)', re.MULTILINE)
    su = re.search(event_pattern, event)
    if su:
        event_type = su.group(10)
        event_params = su.group(11)
        utime = int(su.group(4))
        return utime, event_type, event_params
    else:
        # Error, could not parse the event string.
        log.error("Could not parse event string")
        return None, None, None


if __name__ == "__main__":

    # Get program arguments.
    parser = argparse.ArgumentParser(description="Autobot events scraper.")
    parser.add_argument("-e", "--events", help="Autobot events path.")
    parser.add_argument("-v", "--version", help="Program version.", action="store_true")
    args = parser.parse_args()

    # Default current system path.
    ePath = os.getcwd()

    if args.version:
        print(f"Program version : {settings.app.APP_VERSION}")
    else:
        if args.events:
            ePath = args.events
            
        main(ePath)
