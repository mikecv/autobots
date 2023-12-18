from app_settings import load, week_days

"""
Report data by controller ID.
Report to span all days.
        Args:
            parser:         Event parser data.
            device:         Device (string) to report on.
        Returns:
            Returns         None.
"""

def report_by_device(parser, device):
    print("#"*80)
    print(f"Events for controller {device}")
    print("#"*80)
    for day in week_days:
        print(f"Events for {day}")
        print("="*80)
        for ev in parser.event_data.all_events:
            if ev.device == device and ev.day == day:
                print(f"   {ev.time} : {ev.event_type:20} : {ev.params}")
        print("="*80)
    print("#"*80)
