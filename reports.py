from app_settings import load, week_days

"""
Report data by controller ID.
Report to span all days.
        Args:
            settings        Application settings.
            parser:         Event parser data.
            device:         Device (string) to report on.
        Returns:
            Returns         None.
"""

def report_by_device(settings, parser, device):

    print("#"*80)
    print(f"Events for controller {device}")
    print("#"*80)
    for day in week_days:
        fst_event = False
        # Track number of trips.
        trips = 0
        # Track number of events of different types.
        event_type = {}
        print(f"Events for {day}")
        print("="*80)
        for ev in parser.event_data.all_events:
            # Report on event details.
            if (ev.device == device) and (ev.day == day) and (ev.event_type not in settings.report.EXCEPTIONS):
                # Add trip separator.
                # Separate each trip, i.e. between SIGNON and TRIP events.
                # Don't include reports in exceptions list, i.e. no interest or not supported events.
                if fst_event == True:
                    if ev.event_type == "SIGNON":
                        print("-"*80)
                        # Add an extra trip to the count.
                        trips += 1
                else:
                    fst_event = True
                    if ev.event_type == "SIGNON":
                        # Add an extra trip to the count.
                        trips += 1
                print(f"   {ev.time} : {ev.event_type:20} : {ev.params}")
                # Update count according to event type, don't include trip and exception events.
                if (ev.event_type not in settings.report.TRIP_EVENTS) and (ev.event_type not in settings.report.EXCEPTIONS):
                    if ev.event_type not in event_type:
                        event_type[ev.event_type] = 1
                    else:
                        event_type[ev.event_type] += 1                  
        print("="*80)
        # Print the totalisers for trips and events.
        print(f"Trips : {trips}")
        print("-"*80)
        print(f"Events")
        for evt in event_type:
            print(f"   {evt:15} : {event_type[evt]}")
        print("#"*80)
    print("#"*80)

"""
Report data for specific controller for a specific day.
        Args:
            settings        Application settings.
            parser:         Event parser data.
            day:            Day of week to report on
            device:         Device (string) to report on.
        Returns:
            Returns         None.
"""

def report_by_device_on_day(settings, parser, device, day):
    
    print("#"*80)
    print(f"Events for device {device} on {day}")
    print("#"*80)
    fst_event = False
    # Track number of trips.
    trips = 0
    # Track number of events of different types.
    event_type = {}
    for ev in parser.event_data.all_events:
        # Report on event details.
        if (ev.device == device) and (ev.day.lower() == day.lower()) and (ev.event_type not in settings.report.EXCEPTIONS):
            # Add trip separator.
            # Separate each trip, i.e. between SIGNON and TRIP events.
            # Don't include reports in exceptions list, i.e. no interest or not supported events.
            if fst_event == True:
                if ev.event_type == "SIGNON":
                    print("-"*80)
                    # Add an extra trip to the count.
                    trips += 1
            else:
                fst_event = True
                # Add an extra trip to the count.
                trips += 1
            print(f"   {ev.time} : {ev.event_type:20} : {ev.params}")
            # Update count according to event type, don't include trip and exception events.
            if (ev.event_type not in settings.report.TRIP_EVENTS) and (ev.event_type not in settings.report.EXCEPTIONS):
                if ev.event_type not in event_type:
                    event_type[ev.event_type] = 1
                else:
                    event_type[ev.event_type] += 1                  
    print("="*80)
    # Print the totalisers for trips and events.
    print(f"Trips : {trips}")
    print("-"*80)
    print(f"Events")
    for evt in event_type:
        print(f"   {evt:15} : {event_type[evt]}")
    print("#"*80)
