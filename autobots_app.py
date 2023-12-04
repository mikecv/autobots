"""
Autobot event lists.
"""

from collections import defaultdict
import logging

import dotsi  # type: ignore
import json

import app_settings
from app_logging import setup_logging

def main():

    log = logging.getLogger(__name__)

    # Load application settings.
    settings = dotsi.Dict(app_settings.load("./settings.yaml"))

    # Initialise app name and version from settings.
    app_name = settings.app.APP_NAME
    app_version = settings.app.APP_VERSION

    # Setup the application logger.
    setup_logging(app_name)

    log.info(f"Initialising application: {app_name}, version: {app_version}")

    # Open json file.
    jf = open('./5174-Fr-0000-1.json')
    json_data = json.load(jf)
    for i in json_data['events']:
        print(i)
        log.info(f"Event string : {i}")

if __name__ == "__main__":

    main()
