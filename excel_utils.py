"""
Генерация Excel отчётов.
"""
import uuid
from datetime import datetime

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


def create_report(tasks: list, profile: dict) -> str:
    """
    Создаёт Excel отчёт с задачами и профилем.
    Возвращает путь к файлу.
    """
    if not OPENPYXL_AVAILABLE:
        return None

    wb = Workbook()

    # === Лист задач ===
    ws_tasks = wb.active
    ws_tasks.title = "Задачи"

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="8B008B", end_color="8B008B", fill_type="solid")

    headers = ["#", "Задача", "Дата/Время", "Статус"]
    for col, h in enumerate(headers, 1):
        cell = ws_tasks.cell(row=1, column=col, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for i, task in enumerate(tasks, 1):
        ws_tasks.cell(row=i + 1, column=1, value=i)
        ws_tasks.cell(row=i + 1, column=2, value=task.get("title", ""))
        ws_tasks.cell(row=i + 1, column=3, value=task.get("dt", ""))
        ws_tasks.cell(row=i + 1, column=4, value="Активна")

    ws_tasks.column_dimensions["B"].width = 40
    ws_tasks.column_dimensions["C"].width = 20

    # === Лист профиля ===
    if profile:
        ws_profile = wb.create_sheet("Профиль")
        ws_profile.cell(row=1, column=1, value="Параметр").font = Font(bold=True)
        ws_profile.cell(row=1, column=2, value="Ответ").font = Font(bold=True)
        for i, (k, v) in enumerate(profile.items(), 2):
            ws_profile.cell(row=i, column=1, value=k)
            ws_profile.cell(row=i, column=2, value=str(v))
        ws_profile.column_dimensions["A"].width = 40
        ws_profile.column_dimensions["B"].width = 50

    # === Лист статистики ===
    ws_stat = wb.create_sheet("Статистика")
    ws_stat.cell(row=1, column=1, value="Дата отчёта").font = Font(bold=True)
    ws_stat.cell(row=1, column=2, value=datetime.now().strftime("%Y-%m-%d %H:%M"))
    ws_stat.cell(row=2, column=1, value="Задач всего")
    ws_stat.cell(row=2, column=2, value=len(tasks))

    filepath = f"/tmp/report_{uuid.uuid4().hex[:8]}.xlsx"
    wb.save(filepath)
    return filepath
