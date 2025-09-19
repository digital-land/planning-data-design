import logging
from datetime import datetime

import yaml

logger = logging.getLogger(__name__)


class EventService:
    def __init__(self):
        self.data_file_path = "data/upcoming-events.yml"

    def get_all_events(self):
        try:
            with open(self.data_file_path, "r") as file:
                all_events = yaml.safe_load(file)
                if isinstance(all_events, dict) and "events" in all_events:
                    return all_events["events"]
                return []
        except Exception as e:
            logger.error(f"Error fetching content item: {e}")
            return []

    def get_upcoming_events(self):
        events = self.get_all_events()
        if not events:
            return []

        upcoming_events = [
            event
            for event in events
            if event.get("start_time")
            and event.get("start_time") >= datetime.now().isoformat()
        ]
        return upcoming_events
