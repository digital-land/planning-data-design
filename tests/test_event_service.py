from datetime import datetime, timedelta
from unittest.mock import patch, mock_open
import pytest
from application.services.event_service import EventService


class TestEventService:
    """Test suite for EventService class."""

    @pytest.fixture
    def event_service(self):
        """Create EventService instance with mocked config."""
        return EventService()

    @patch("builtins.open", new_callable=mock_open, read_data="irrelevant")
    @patch("yaml.safe_load")
    def test_get_all_events_success(self, mock_yaml_load, mock_file, event_service):
        """Test get_all_events successfully retrieves events from YAML."""
        mock_events = [
            {"id": 1, "name": "Event 1", "start_time": "2024-12-01T10:00:00"},
            {"id": 2, "name": "Event 2", "start_time": "2024-12-15T14:00:00"},
        ]
        mock_yaml_load.return_value = {"events": mock_events}

        result = event_service.get_all_events()

        mock_file.assert_called_once_with("data/upcoming-events.yml", "r")
        mock_yaml_load.assert_called_once()
        assert result == mock_events

    @patch("builtins.open", new_callable=mock_open, read_data="irrelevant")
    @patch("yaml.safe_load")
    def test_get_all_events_missing_data_key(
        self, mock_yaml_load, mock_file, event_service
    ):
        """Test get_all_events handles missing data key gracefully."""
        mock_yaml_load.return_value = {"something": "else"}

        result = event_service.get_all_events()

        assert result == []

    @patch("builtins.open", new_callable=mock_open, read_data="irrelevant")
    @patch("yaml.safe_load")
    def test_get_all_events_missing_events_key(
        self, mock_yaml_load, mock_file, event_service
    ):
        """Test get_all_events handles missing events key gracefully."""
        mock_yaml_load.return_value = {"data": {"other": "data"}}

        result = event_service.get_all_events()

        assert result == []

    @patch("builtins.open", new_callable=mock_open, read_data="irrelevant")
    @patch("yaml.safe_load", side_effect=Exception("File error"))
    @patch("application.services.event_service.logger")
    def test_get_all_events_file_error(
        self, mock_logger, mock_yaml_load, mock_file, event_service
    ):
        """Test get_all_events handles file errors."""
        result = event_service.get_all_events()

        assert result == []
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "Error fetching content item" in error_call_args
        assert "File error" in error_call_args

    @patch.object(EventService, "get_all_events")
    def test_get_upcoming_events_success(self, mock_get_all_events, event_service):
        """Test get_upcoming_events filters events correctly."""
        now = datetime.now()
        past_time = (now - timedelta(days=1)).isoformat()
        future_time1 = (now + timedelta(days=1)).isoformat()
        future_time2 = (now + timedelta(days=7)).isoformat()

        mock_events = [
            {"id": 1, "name": "Past Event", "start_time": past_time},
            {"id": 2, "name": "Future Event 1", "start_time": future_time1},
            {"id": 3, "name": "Future Event 2", "start_time": future_time2},
        ]
        mock_get_all_events.return_value = mock_events

        with patch("application.services.event_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = now
            result = event_service.get_upcoming_events()

        # Should only return future events
        assert len(result) == 2
        assert result[0]["name"] == "Future Event 1"
        assert result[1]["name"] == "Future Event 2"

    @patch.object(EventService, "get_all_events")
    def test_get_upcoming_events_no_events(self, mock_get_all_events, event_service):
        """Test get_upcoming_events when no events are returned."""
        mock_get_all_events.return_value = []
        result = event_service.get_upcoming_events()

        assert result == []

    @patch.object(EventService, "get_all_events")
    def test_get_upcoming_events_empty_list(self, mock_get_all_events, event_service):
        """Test get_upcoming_events when empty list is returned."""
        mock_get_all_events.return_value = []
        result = event_service.get_upcoming_events()

        assert result == []

    @patch.object(EventService, "get_all_events")
    def test_get_upcoming_events_no_start_time(
        self, mock_get_all_events, event_service
    ):
        """Test get_upcoming_events handles events without start_time."""
        mock_events = [
            {"id": 1, "name": "Event without start_time"},
            {
                "id": 2,
                "name": "Event with start_time",
                "start_time": "2024-12-01T10:00:00",
            },
        ]
        mock_get_all_events.return_value = mock_events

        with patch("application.services.event_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 11, 1)
            result = event_service.get_upcoming_events()

        # Should only return the event with start_time that's in the future
        assert len(result) == 1
        assert result[0]["name"] == "Event with start_time"

    @patch.object(EventService, "get_all_events")
    def test_get_upcoming_events_edge_case_same_time(
        self, mock_get_all_events, event_service
    ):
        """Test get_upcoming_events with events at exactly current time."""
        now = datetime.now()
        exact_time = now.isoformat()

        mock_events = [
            {"id": 1, "name": "Exact Time Event", "start_time": exact_time},
        ]
        mock_get_all_events.return_value = mock_events

        with patch("application.services.event_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = now
            result = event_service.get_upcoming_events()

        # Event at exact current time should be included (>= comparison)
        assert len(result) == 1
        assert result[0]["name"] == "Exact Time Event"
