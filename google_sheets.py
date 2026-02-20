import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

def get_sheet():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scope
        )
        client = gspread.authorize(creds)
        return client.open("OlyaBot").sheet1
    except Exception as e:
        print(f"Sheets error: {e}")
        return None

def save_to_sheet(text: str):
    sheet = get_sheet()
    if sheet:
        sheet.append_row([text])
