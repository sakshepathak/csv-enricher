import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import json
from typing import Any

def authenticate_gspread(creds_file: Any) -> gspread.Client:
    """
    Authenticate with Google Sheets API using the provided credentials file.

    Args:
        creds_file (Any): The uploaded credentials file (Streamlit UploadedFile object).

    Returns:
        gspread.Client: An authenticated gspread client.
    """
    scope: list[str] = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    creds_dict: dict = json.load(creds_file)
    creds: ServiceAccountCredentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client: gspread.Client = gspread.authorize(creds)
    return client

def load_google_sheet(client: gspread.Client, sheet_url: str) -> pd.DataFrame:
    """
    Load data from a Google Sheet using an authenticated client.

    Args:
        client (gspread.Client): The authenticated gspread client.
        sheet_url (str): The URL of the Google Sheet.

    Returns:
        pd.DataFrame: DataFrame containing the sheet's data.
    """
    sheet: gspread.Spreadsheet = client.open_by_url(sheet_url)
    worksheet: gspread.Worksheet = sheet.get_worksheet(0)  # Get the first sheet
    data: list[dict] = worksheet.get_all_records()
    df: pd.DataFrame = pd.DataFrame(data)
    return df


def write_to_google_sheet(client: gspread.Client, sheet_url: str, df: pd.DataFrame) -> None:
    """
    Write a pandas DataFrame to a Google Sheet.

    Args:
        client (gspread.Client): The authenticated gspread client.
        sheet_url (str): The URL of the Google Sheet.
        df (pd.DataFrame): DataFrame to write to the sheet.
    """
    try:
        spreadsheet = client.open_by_url(sheet_url)
        worksheet = spreadsheet.get_worksheet(0)  # Get the first sheet
        worksheet.clear()  # Clear existing content
        set_with_dataframe(worksheet, df)  # Write the new data
    except Exception as e:
        raise ValueError(f"Failed to write to Google Sheet: {e}")