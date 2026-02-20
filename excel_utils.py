from openpyxl import Workbook

def create_report(data: list):
    try:
        wb = Workbook()
        ws = wb.active
        ws.append(["Дата", "Событие", "Комментарий"])
        
        for row in data:
            ws.append(row)
        
        wb.save("report.xlsx")
        return "report.xlsx"
    except Exception as e:
        print(f"Excel error: {e}")
        return None
