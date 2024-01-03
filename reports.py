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
        print(f"Events for {day}")
        print("="*80)
        for ev in parser.event_data.all_events:
            # Report on event details.
            if (ev.device == device) and (ev.day == day) and (ev.event_type not in settings.report.EXECEPTIONS):
                # Add trip separator.
                # Separate each trip, i.e. between SIGNON and TRIP events.
                # Don't include reports in exceptions list, i.e. no interest or not supported events.
                if fst_event == True:
                    if ev.event_type == "SIGNON":
                        print("-"*80)
                else:
                    fst_event = True
                print(f"   {ev.time} : {ev.event_type:20} : {ev.params}")
        print("="*80)
    print("#"*80)
