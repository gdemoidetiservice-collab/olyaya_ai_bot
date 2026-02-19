"""
Генерация .ics файлов для импорта в Apple Calendar / iOS.
"""
from datetime import datetime
import uuid


def create_ics(title: str, dt: datetime = None, description: str = "") -> str:
    """
    Создаёт содержимое .ics файла.
    Возвращает строку с содержимым файла.
    """
    if dt is None:
        dt = datetime.now()

    uid = str(uuid.uuid4())
    now_str = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dt_str = dt.strftime("%Y%m%dT%H%M%S")

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//OlyaBot//OlyaBot//RU
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{now_str}
DTSTART:{dt_str}
DTEND:{dt_str}
SUMMARY:{title}
DESCRIPTION:{description}
END:VEVENT
END:VCALENDAR"""

    return ics_content


def save_ics(title: str, dt: datetime = None, description: str = "") -> str:
    """Сохраняет .ics файл и возвращает путь к нему."""
    content = create_ics(title, dt, description)
    filepath = f"/tmp/event_{uuid.uuid4().hex[:8]}.ics"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath
