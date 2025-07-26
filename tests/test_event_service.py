from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError

from application.services.event_service import EventService


class TestEventService:
    """Test suite for EventService class."""

    @pytest.fixture
    def mock_config(self):
        """Mock Config with test CMS URL."""
        with patch("application.services.event_service.Config") as mock_config_class:
            mock_config = Mock()
            mock_config.CMS_URL = "https://test-cms.example.com"
            mock_config_class.return_value = mock_config
            yield mock_config

    @pytest.fixture
    def event_service(self, mock_config):
        """Create EventService instance with mocked config."""
        return EventService()

    def test_init(self, event_service, mock_config):
        """Test EventService initialization sets cms_url from config."""
        assert event_service.cms_url == "https://test-cms.example.com"

    def test_get_cms_endpoint(self, event_service):
        """Test get_cms_endpoint returns correct URL."""
        expected_url = (
            "https://test-cms.example.com/api/v1/collections/data_design/events"
        )
        assert event_service.get_cms_endpoint() == expected_url

    @patch("application.services.event_service.get")
    def test_get_all_events_success(self, mock_get, event_service):
        """Test get_all_events successfully retrieves events."""
        # Mock response data
        mock_events = [
            {"id": 1, "name": "Event 1", "start_time": "2024-12-01T10:00:00"},
            {"id": 2, "name": "Event 2", "start_time": "2024-12-15T14:00:00"},
        ]
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"events": mock_events}}
        mock_get.return_value = mock_response

        result = event_service.get_all_events()

        mock_get.assert_called_once_with(event_service.get_cms_endpoint(), timeout=10)
        assert result == mock_events

    @patch("application.services.event_service.get")
    def test_get_all_events_missing_data_key(self, mock_get, event_service):
        """Test get_all_events handles missing data key gracefully."""
        mock_response = Mock()
        mock_response.json.return_value = {"something": "else"}
        mock_get.return_value = mock_response

        result = event_service.get_all_events()

        assert result == []

    @patch("application.services.event_service.get")
    def test_get_all_events_missing_events_key(self, mock_get, event_service):
        """Test get_all_events handles missing events key gracefully."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"other": "data"}}
        mock_get.return_value = mock_response

        result = event_service.get_all_events()

        assert result == []

    @patch("application.services.event_service.get")
    @patch("application.services.event_service.logger")
    def test_get_all_events_connection_error(
        self, mock_logger, mock_get, event_service
    ):
        """Test get_all_events handles connection errors."""
        mock_get.side_effect = ConnectionError("Connection failed")

        result = event_service.get_all_events()

        assert result == []
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "Error fetching CMS content item" in error_call_args
        assert "Connection failed" in error_call_args

    @patch("application.services.event_service.get")
    @patch("application.services.event_service.logger")
    def test_get_all_events_json_decode_error(
        self, mock_logger, mock_get, event_service
    ):
        """Test get_all_events handles JSON decode errors."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = event_service.get_all_events()

        assert result == []
        mock_logger.error.assert_called_once()

    @patch.object(EventService, "get_all_events")
    def test_get_upcoming_events_success(self, mock_get_all_events, event_service):
        """Test get_upcoming_events filters events correctly."""
        # Create test data with past and future events
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
