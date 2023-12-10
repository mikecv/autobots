from datetime import datetime
import json
import logging
import os
import re

import events


class Events_parser:

    def __init__(self, logger:logging.Logger, root_dir: str, dev_map) -> None:
        """
        Class for events parsing.
        Args:
            logger:         Appliction logger.
            root_dir:       Root directory to parse.
            dev_map:        Device map.
        Returns:
            Returns         None.
        """

        # Application logger.
        self.log = logger
    
        # Root path to parse, and device mapping file.
        self.root_dir = root_dir
        self.dev_map = dev_map

        # Parse the device mapping file.
        self.log.info(f"Reading device mapping file: {self.dev_map}")
        self.dev_map = self.get_device_mapping(self.dev_map)
        if self.dev_map is None:
            self.log.error(f"Failed to process device mapping file.")
            exit(-1)

        # Create object to hold all events data.
        self.event_data = events.All_events()

    def traverse_path(self):
        self.log.debug(f"Traversing root path: {self.root_dir}")
        # Traverse through folders starting at root.
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    self.process_json_file(file_path)

    def process_json_file(self, file_path):
        # Parse the JSON file of trips.
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                # Process the json event data.
                self.log.info(f"Processing JSON file: {file_path}")
                # Get period for trip.
                trip_period = data['category']
                self.log.debug(f"Process period: {trip_period}")
                # Get the trip details.
                cntrl_id = data['_trip_info']['controller_id']
                self.log.debug(f"Controller Id: {cntrl_id}")
                cntrl_id = data['_trip_info']['controller_id']
                dev_id = self.dev_map[cntrl_id]
                self.log.debug(f"Mapped device Id: {dev_id}")
                # Process event data in the trip.
                for event in data['events']:
                    self.log.debug(f"Trip event string: {event}")
                    utime, event_type, event_params = self.parse_event(event)
                    event_day = datetime.utcfromtimestamp(utime).strftime('%A')
                    event_time = datetime.utcfromtimestamp(utime).strftime('%H:%M:%S')
                    self.log.debug(f"Found event at: {utime} : {event_day} - {event_time}")
                    self.log.debug(f"Found event: {event_type}")
                    self.log.debug(f"Event arguments: {event_params}")
                    # Create the event object and add to list of all events.
                    this_event = events.Event(dev_id, event_day, event_time, event_type, event_params)
                    self.event_data.add_event(this_event)
            except json.JSONDecodeError as e:
                self.log.error(f"Error decoding JSON event file: {file_path}: {e}")

    def get_device_mapping(self, dmap):  
        # Open JSON device mapping file and create dictionary
        with open(dmap, 'r') as m_file:
            try:
                mmap = json.load(m_file)
                device_map = {}
                # Populate dictionary with device mappings.
                for device in mmap["controllers"]:
                    device_map[device] = mmap["controllers"][device]["id"]
                self.log.debug(f"Device mapping file: {device_map}")
                return device_map
            except json.JSONDecodeError as e:
                self.log.error(f"Error decoding machine mapping file: {e}")
                return None

    def parse_event(self, event):
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
            self.log.error("Could not parse event string")
            return None, None, None
