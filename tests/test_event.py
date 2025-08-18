"""Tests for the event module."""

from timetree_exporter.event import (
    TimeTreeEvent,
    TimeTreeEventType,
    TimeTreeEventCategory,
)


def test_event_creation(normal_event_data):
    """Test creating a TimeTreeEvent."""
    event = TimeTreeEvent(
        uuid=normal_event_data["uuid"],
        title=normal_event_data["title"],
        created_at=normal_event_data["created_at"],
        updated_at=normal_event_data["updated_at"],
        note=normal_event_data["note"],
        location=normal_event_data["location"],
        location_lat=normal_event_data["location_lat"],
        location_lon=normal_event_data["location_lon"],
        url=normal_event_data["url"],
        start_at=normal_event_data["start_at"],
        start_timezone=normal_event_data["start_timezone"],
        end_at=normal_event_data["end_at"],
        end_timezone=normal_event_data["end_timezone"],
        all_day=normal_event_data["all_day"],
        alerts=normal_event_data["alerts"],
        recurrences=normal_event_data["recurrences"],
        parent_id=normal_event_data["parent_id"],
        event_type=normal_event_data["type"],
        category=normal_event_data["category"],
    )

    assert event.uuid == normal_event_data["uuid"]
    assert event.title == normal_event_data["title"]
    assert event.created_at == normal_event_data["created_at"]
    assert event.updated_at == normal_event_data["updated_at"]
    assert event.note == normal_event_data["note"]
    assert event.location == normal_event_data["location"]
    assert event.location_lat == normal_event_data["location_lat"]
    assert event.location_lon == normal_event_data["location_lon"]
    assert event.url == normal_event_data["url"]
    assert event.start_at == normal_event_data["start_at"]
    assert event.start_timezone == normal_event_data["start_timezone"]
    assert event.end_at == normal_event_data["end_at"]
    assert event.end_timezone == normal_event_data["end_timezone"]
    assert event.all_day == normal_event_data["all_day"]
    assert event.alerts == normal_event_data["alerts"]
    assert event.recurrences == normal_event_data["recurrences"]
    assert event.parent_id == normal_event_data["parent_id"]
    assert event.event_type == normal_event_data["type"]
    assert event.category == normal_event_data["category"]


def test_from_dict(normal_event_data):
    """Test creating a TimeTreeEvent from a dictionary."""
    event = TimeTreeEvent.from_dict(normal_event_data)

    assert event.uuid == normal_event_data["uuid"]
    assert event.title == normal_event_data["title"]
    assert event.created_at == normal_event_data["created_at"]
    assert event.updated_at == normal_event_data["updated_at"]
    assert event.note == normal_event_data["note"]
    assert event.location == normal_event_data["location"]
    assert event.location_lat == normal_event_data["location_lat"]
    assert event.location_lon == normal_event_data["location_lon"]
    assert event.url == normal_event_data["url"]
    assert event.start_at == normal_event_data["start_at"]
    assert event.start_timezone == normal_event_data["start_timezone"]
    assert event.end_at == normal_event_data["end_at"]
    assert event.end_timezone == normal_event_data["end_timezone"]
    assert event.all_day == normal_event_data["all_day"]
    assert event.alerts == normal_event_data["alerts"]
    assert event.recurrences == normal_event_data["recurrences"]
    assert event.parent_id == normal_event_data["parent_id"]
    assert event.event_type == normal_event_data["type"]
    assert event.category == normal_event_data["category"]


def test_str_representation(normal_event_data):
    """Test the string representation of a TimeTreeEvent."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    assert str(event) == normal_event_data["title"]


def test_event_types():
    """Test the TimeTreeEventType enumeration."""
    assert TimeTreeEventType.NORMAL == 0
    assert TimeTreeEventType.BIRTHDAY == 1


def test_event_categories():
    """Test the TimeTreeEventCategory enumeration."""
    assert TimeTreeEventCategory.NORMAL == 1
    assert TimeTreeEventCategory.MEMO == 2


def test_get_ical_color():
    """Test the get_ical_color method."""
    # Test with valid label_ids
    event_data = {
        "uuid": "test-uuid",
        "title": "Test Event",
        "created_at": 1234567890000,
        "updated_at": 1234567890000,
        "note": "",
        "location": "",
        "location_lat": None,
        "location_lon": None,
        "url": "",
        "start_at": 1234567890000,
        "start_timezone": "UTC",
        "end_at": 1234567890000,
        "end_timezone": "UTC",
        "all_day": False,
        "alerts": [],
        "recurrences": [],
        "parent_id": None,
        "type": 0,
        "category": 1,
        "label_id": "1"
    }
    
    event = TimeTreeEvent.from_dict(event_data)
    assert event.get_ical_color() == "#08808F"  # Teal
    
    # Test different colors
    test_cases = [
        ("1", "#08808F"),  # Teal
        ("2", "#6C5E58"),  # Grey
        ("3", "#1963A4"),  # Blue
        ("4", "#AF3D19"),  # Deep Orange
        ("5", "#2C377C"),  # Dark Blue
        ("6", "#A62E2E"),  # Plum
        ("7", "#681D7B"),  # Orchid
        ("8", "#B46604"),  # Orange
        ("9", "#5B8232"),  # Green
    ]
    
    for label_id, expected_color in test_cases:
        event_data["label_id"] = label_id
        event = TimeTreeEvent.from_dict(event_data)
        assert event.get_ical_color() == expected_color
    
    # Test with None label_id
    event_data["label_id"] = None
    event = TimeTreeEvent.from_dict(event_data)
    assert event.get_ical_color() is None
    
    # Test with invalid label_id
    event_data["label_id"] = "10"  # Out of range
    event = TimeTreeEvent.from_dict(event_data)
    assert event.get_ical_color() is None
    
    # Test with invalid string
    event_data["label_id"] = "invalid"
    event = TimeTreeEvent.from_dict(event_data)
    assert event.get_ical_color() is None
