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
                # Get the json file number as used to work out time offset.
                # Offset calculated from first file in series.
                file_num = file.split('-')[3].split('.')[0]
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    self.process_json_file(file_path, int(file_num))

    def process_json_file(self, file_path, file_num):
        # Parse the JSON file of trips.
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                # Process the json event data.
                self.log.info(f"Processing JSON file: {file_path}")
                # Get period for trip.
                trip_period = data['category']
                self.log.debug(f"Process period: {trip_period}")
                period_day = trip_period.split('; ')[0]
                period_time = trip_period.split('; ')[1].split()[0]
                period_time = int(period_time) * 36
                # Get the trip details.
                cntrl_id = data['_trip_info']['controller_id']
                self.log.debug(f"Controller Id: {cntrl_id}")
                cntrl_id = data['_trip_info']['controller_id']
                dev_id = self.dev_map[cntrl_id]
                self.log.debug(f"Mapped device Id: {dev_id}")
                # Process event data in the trip.
                ev_first = True
                for event in data['events']:
                    # The time of the event comes from the period in the file name.
                    # The time of events is the offset from the previous event in the file.
                    # The starting time of the first event in the first file comes from the start of
                    # the period.
                    self.log.debug(f"Trip event string: {event}")

                    # Parse the event string.
                    utime, event_type, event_params = self.parse_event(event)

                    # Work out the starting time for the offset.
                    # Check if this is the first file number in the series.
                    if file_num == 1:
                        # First file so get from start of the period.
                        # Followed by time offset from previous event.
                        if ev_first is True:
                            st_time = period_time
                            st_evt_time = utime
                            fst_offset = st_time
                            ev_first = False
                        else:
                            st_time = fst_offset + utime - st_evt_time
                            st_evt_time = utime
                    else:
                        # Not the first file so get start time from previous event.
                        st_time = utime - st_evt_time
                        st_evt_time = utime

                    event_day = period_day
                    event_time = datetime.utcfromtimestamp(st_time).strftime('%H:%M:%S')
                    self.log.debug(f"Found event for controller: {dev_id}")
                    self.log.debug(f"Found event at: {event_day} - {event_time}")
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
