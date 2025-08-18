"""Tests for the formatter module."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


from icalendar import Event
from icalendar.prop import vDuration
from timetree_exporter.event import (
    TimeTreeEvent,
    TimeTreeEventType,
    TimeTreeEventCategory,
)
from timetree_exporter.formatter import ICalEventFormatter
from timetree_exporter.utils import convert_timestamp_to_datetime


def test_formatter_properties(normal_event_data):
    """Test the properties of the ICalEventFormatter."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    formatter = ICalEventFormatter(event)

    assert formatter.uid == normal_event_data["uuid"]
    assert formatter.summary == normal_event_data["title"]
    assert formatter.description == normal_event_data["note"]
    assert formatter.location == normal_event_data["location"]
    assert formatter.url == normal_event_data["url"]
    assert formatter.related_to == normal_event_data["parent_id"]

    # Test created time
    created_dt = convert_timestamp_to_datetime(
        normal_event_data["created_at"] / 1000, ZoneInfo("UTC")
    )
    assert formatter.created.dt == created_dt

    # Test last modified time
    modified_dt = convert_timestamp_to_datetime(
        normal_event_data["updated_at"] / 1000, ZoneInfo("UTC")
    )
    assert formatter.last_modified.dt == modified_dt

    # Test geo
    assert formatter.geo.latitude == float(normal_event_data["location_lat"])
    assert formatter.geo.longitude == float(normal_event_data["location_lon"])

    # Test datetime properties
    start_dt = convert_timestamp_to_datetime(
        normal_event_data["start_at"] / 1000,
        ZoneInfo(normal_event_data["start_timezone"]),
    )
    end_dt = convert_timestamp_to_datetime(
        normal_event_data["end_at"] / 1000, ZoneInfo(normal_event_data["end_timezone"])
    )
    assert formatter.dtstart.dt == start_dt
    assert formatter.dtend.dt == end_dt

    # Test alarms
    alarms = formatter.alarms
    assert len(alarms) == 2
    assert alarms[0]["action"] == "DISPLAY"
    assert alarms[0]["description"] == "Reminder"
    assert alarms[0]["trigger"] == vDuration(timedelta(minutes=-15))
    assert alarms[1]["action"] == "DISPLAY"
    assert alarms[1]["description"] == "Reminder"
    assert alarms[1]["trigger"] == vDuration(timedelta(minutes=-60))


def test_to_ical_normal_event(normal_event_data):
    """Test converting a normal TimeTreeEvent to an iCal event."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert isinstance(ical_event, Event)
    assert ical_event["uid"] == normal_event_data["uuid"]
    assert ical_event["summary"] == normal_event_data["title"]
    assert ical_event["description"] == normal_event_data["note"]
    assert ical_event["location"] == normal_event_data["location"]
    assert ical_event["url"] == normal_event_data["url"]
    assert ical_event["related-to"] == normal_event_data["parent_id"]

    # Verify that the event has alarms
    components = list(ical_event.subcomponents)
    assert len(components) == 2  # Two alarms
    assert all(component.name == "VALARM" for component in components)

    # Verify recurrence rule
    assert "RRULE" in ical_event
    assert ical_event["RRULE"]["FREQ"] == ["WEEKLY"]
    assert ical_event["RRULE"]["COUNT"] == [5]


def test_to_ical_birthday_event(birthday_event_data):
    """Test converting a birthday TimeTreeEvent to an iCal event."""
    event = TimeTreeEvent.from_dict(birthday_event_data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    # Birthday events should be skipped
    assert ical_event is None


def test_to_ical_memo_event(memo_event_data):
    """Test converting a memo TimeTreeEvent to an iCal event."""
    event = TimeTreeEvent.from_dict(memo_event_data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    # Memo events should be skipped
    assert ical_event is None


def test_all_day_event(birthday_event_data):
    """Test formatting an all-day event."""
    # Modify to a normal event that's all-day (not a birthday)
    all_day_data = birthday_event_data.copy()
    all_day_data["type"] = TimeTreeEventType.NORMAL

    event = TimeTreeEvent.from_dict(all_day_data)
    formatter = ICalEventFormatter(event)

    # Test that dtstart and dtend use vDate instead of vDatetime for all-day events

    assert isinstance(formatter.dtstart.dt, datetime)
    assert (
        formatter.dtstart.dt.date()
        == convert_timestamp_to_datetime(
            all_day_data["start_at"] / 1000, ZoneInfo(all_day_data["start_timezone"])
        ).date()
    )

    # Check to_ical produces a valid event
    ical_event = formatter.to_ical()
    assert isinstance(ical_event, Event)
    assert ical_event["summary"] == all_day_data["title"]


def test_no_alarms_location_url(normal_event_data):
    """Test event formatting without optional fields."""
    # Create an event without alarms, location, and URL
    data = normal_event_data.copy()
    data["alerts"] = None
    data["location"] = ""
    data["location_lat"] = None
    data["location_lon"] = None
    data["url"] = ""

    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)

    assert not formatter.alarms
    assert formatter.location is None
    assert formatter.geo is None
    assert formatter.url is None

    # Check the iCal event
    ical_event = formatter.to_ical()
    assert "location" not in ical_event
    assert "geo" not in ical_event
    assert "url" not in ical_event

    # Verify no alarms were added
    components = list(ical_event.subcomponents)
    assert len(components) == 0


def test_different_timezones(normal_event_data):
    """Test event with different start and end timezones."""
    # Create an event with different start and end timezones
    data = normal_event_data.copy()
    data["start_timezone"] = "America/New_York"  # EDT/EST
    data["end_timezone"] = "Asia/Tokyo"  # JST

    # Set specific timestamps
    ny_time = datetime(2023, 6, 15, 10, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    data["start_at"] = int(ny_time.timestamp() * 1000)

    tokyo_time = datetime(2023, 6, 16, 8, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
    data["end_at"] = int(tokyo_time.timestamp() * 1000)

    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)

    # Test timezone properties are correctly set
    assert formatter.dtstart.dt.tzinfo.key == "America/New_York"
    assert formatter.dtend.dt.tzinfo.key == "Asia/Tokyo"

    # Verify the actual datetime values
    assert formatter.dtstart.dt == ny_time
    assert formatter.dtend.dt == tokyo_time

    # Convert both to UTC for comparison of the actual time (not just representation)
    start_utc = formatter.dtstart.dt.astimezone(ZoneInfo("UTC"))
    end_utc = formatter.dtend.dt.astimezone(ZoneInfo("UTC"))

    # Verify the time difference is preserved
    # Tokyo time is 13 hours ahead of New York during EDT
    expected_hours_diff = (
        tokyo_time.astimezone(ZoneInfo("UTC")) - ny_time.astimezone(ZoneInfo("UTC"))
    ).total_seconds() / 3600
    actual_hours_diff = (end_utc - start_utc).total_seconds() / 3600
    assert actual_hours_diff == expected_hours_diff

    # Check iCal event preserves timezone information
    ical_event = formatter.to_ical()
    assert ical_event["dtstart"].dt.tzinfo.key == "America/New_York"
    assert ical_event["dtend"].dt.tzinfo.key == "Asia/Tokyo"


def test_color_property(normal_event_data):
    """Test the color property of the ICalEventFormatter."""
    # Test with a specific label_id
    event_data = normal_event_data.copy()
    event_data["label_id"] = "3"  # Blue
    
    event = TimeTreeEvent.from_dict(event_data)
    formatter = ICalEventFormatter(event)
    
    assert formatter.color == "#45B7D1"  # Blue
    
    # Test without label_id
    event_data["label_id"] = None
    event = TimeTreeEvent.from_dict(event_data)
    formatter = ICalEventFormatter(event)
    
    assert formatter.color is None


def test_to_ical_with_color(normal_event_data):
    """Test converting a TimeTreeEvent with color to an iCal event."""
    # Test with color
    event_data = normal_event_data.copy()
    event_data["label_id"] = "5"  # Yellow
    
    event = TimeTreeEvent.from_dict(event_data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()
    
    assert "color" in ical_event
    assert ical_event["color"] == "#FFEAA7"  # Yellow
    
    # Test without color
    event_data["label_id"] = None
    event = TimeTreeEvent.from_dict(event_data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()
    
    assert "color" not in ical_event


def test_multi_day_all_day_event():
    """Test that multi-day all-day events have correct end date (RFC 5545 compliant)."""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    
    # Create a 3-day all-day event (Monday to Wednesday inclusive)
    # Start: 2023-06-12 (Monday)
    # End should be: 2023-06-15 (Thursday) - exclusive end for all-day events
    start_date = datetime(2023, 6, 12, 0, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
    end_date = datetime(2023, 6, 14, 23, 59, 59, tzinfo=ZoneInfo("Europe/Berlin"))  # Wednesday end
    
    event_data = {
        "uuid": "test-uuid-multiday",
        "title": "Mehrtägiger Termin",
        "created_at": 1686528000000,
        "updated_at": 1686528000000,
        "note": "",
        "location": "",
        "location_lat": None,
        "location_lon": None,
        "url": "",
        "start_at": int(start_date.timestamp() * 1000),
        "start_timezone": "Europe/Berlin",
        "end_at": int(end_date.timestamp() * 1000),
        "end_timezone": "Europe/Berlin", 
        "all_day": True,
        "alerts": None,
        "recurrences": None,
        "parent_id": "",
        "type": TimeTreeEventType.NORMAL,
        "category": TimeTreeEventCategory.NORMAL,
    }
    
    event = TimeTreeEvent.from_dict(event_data)
    formatter = ICalEventFormatter(event)
    
    # For all-day events, dtstart should be the actual start date
    assert formatter.dtstart.dt.date() == start_date.date()  # Monday
    
    # For all-day events, dtend should be the day AFTER the last day (RFC 5545)
    # Since the event runs Mon-Wed, end should be Thursday
    expected_end_date = (end_date + timedelta(days=1)).date()  # Thursday 
    assert formatter.dtend.dt.date() == expected_end_date
    
    # Convert to iCal and verify
    ical_event = formatter.to_ical()
    assert ical_event["dtstart"].dt.date() == start_date.date()
    assert ical_event["dtend"].dt.date() == expected_end_date
