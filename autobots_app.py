"""
Autobot event lists.
"""

import argparse
import dotsi  # type: ignore
import json
import logging
import os

import app_settings
from app_logging import setup_logging


log = logging.getLogger(__name__)

# Load application settings.
settings = dotsi.Dict(app_settings.load("./settings.yaml"))

# Initialise app name and version from settings.
app_name = settings.app.APP_NAME
app_version = settings.app.APP_VERSION


def main(ePath):

    # log = logging.getLogger(__name__)

    # # Load application settings.
    # settings = dotsi.Dict(app_settings.load("./settings.yaml"))

    # # Initialise app name and version from settings.
    # app_name = settings.app.APP_NAME
    # app_version = settings.app.APP_VERSION

    # Setup the application logger.
    setup_logging(app_name)

    log.info(f"Initialising application: {app_name}, version: {app_version}")

    # # Open json file.
    # jf = open('./5174-Fr-0000-1.json')
    # json_data = json.load(jf)
    # for i in json_data['events']:
    #     print(i)
    #     log.info(f"Event string : {i}")

    log.info(f"Events path: {ePath}")
    print(f"Events path: {ePath}")

def process_json_file(file_path):
    with open(file_path, 'r') as file:
        try:
            data = json.load(file)
            # Do something with the JSON data
            print(f"Processing JSON file: {file_path}")
            print(data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {file_path}: {e}")

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
        print(f"Program version : {app_version}")
    else:
        if args.events:
            ePath = args.events
            
        main(ePath)
