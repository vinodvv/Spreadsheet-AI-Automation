import os
from googleapiclient.discovery import build
from dotenv import load_dotenv


def load_credentials():
    """Load credentials from .env file"""
    load_dotenv()

    google_api_key = os.getenv("GOOGLE_API_KEY")
    spreadsheet_id=os.getenv("SPREADSHEET_ID")
    sheet_name=os.getenv("SHEET_NAME")
    return google_api_key, spreadsheet_id, sheet_name

def get_spreadsheet_data(google_api_key, spreadsheet_id, sheet_name):
    """Fetch spreadsheet data"""
    service = build('sheets', 'v4', developerKey=google_api_key)
    results = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()['values']
    return results


if __name__ == "__main__":
    google_api_key, spreadsheet_id, sheet_name = load_credentials()

    rows = get_spreadsheet_data(google_api_key, spreadsheet_id, sheet_name)
    print(rows)
