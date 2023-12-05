"""
Autobot event lists.
"""

import argparse
import dotsi  # type: ignore
import json
import logging
import logging.handlers
import os
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
    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
            # Process the json event data.
            log.info(f"Processing JSON file: {file_path}")
            for i in data['events']:
                log.info(i)
        except json.JSONDecodeError as e:
            log.errpr(f"Error decoding JSON in file {file_path}: {e}")

def traverse_directory(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                process_json_file(file_path)

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
