class Event:

    def __init__(self, device: str, day: str, time: str, event_type: str, params: str) -> None:
        """
        Class of an event instance.
        Args:
            device:         The device's serial no.
            day:            The day of the week the event occurred.
            time:           The time of day for the event.

            params:         The paramaters for the event.
        Returns:
            Returns         None.
        """

        self.device = device
        self.day = day
        self.time = time
        self.event_type = event_type
        self.params = params


class All_events:

    def __init__(self) -> None:
        """
        Class of all events in all trips.
        Args:
        Returns:
            Returns         None.
        """

        # List of all events.
        self.all_events = []

    def add_event(self, new_event: Event):
        """
        Add new event to list of all events.
        """

        self.all_events.append(new_event)
    