import logging
from datetime import datetime

from requests import RequestException, get

from application.config import Config

logger = logging.getLogger(__name__)


class EventService:
    def __init__(self):
        self.cms_url = Config().CMS_URL

    def get_cms_endpoint(self):
        return f"{self.cms_url}/api/v1/collections/data_design/events"

    def get_all_events(self):
        try:
            response = get(self.get_cms_endpoint(), timeout=10)
            response.raise_for_status()
            all_events = response.json()
            return all_events.get("data", {}).get("events", [])
        except (RequestException, ValueError) as e:
            logger.error(
                f"Error fetching CMS content item for {self.get_cms_endpoint()}: {e}"
            )
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
