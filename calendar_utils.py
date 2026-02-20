from ics import Calendar, Event
from datetime import datetime

def create_event(title: str, date_str: str, time_str: str = "12:00"):
    try:
        c = Calendar()
        e = Event()
        e.name = title
        
        date_parts = date_str.split(".")
        if len(date_parts) == 3:
            day, month, year = map(int, date_parts)
            hour, minute = map(int, time_str.split(":"))
            event_date = datetime(year, month, day, hour, minute)
            e.begin = event_date
        
        c.events.add(e)
        
        with open("event.ics", "w") as f:
            f.writelines(c)
        return "event.ics"
    except Exception as e:
        print(f"Calendar error: {e}")
        return None
