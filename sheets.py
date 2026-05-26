from __future__ import annotations
import streamlit as st
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
    _gspread_available = True
except ImportError:
    _gspread_available = False


def log_opportunity(opp_number: str) -> bool:
    """
    Append opportunity number + timestamp to Google Sheets.
    Returns True on success, False if not configured or on error.
    """
    if not _gspread_available:
        return False

    try:
        try:
            creds_info = dict(st.secrets["gcp_service_account"])
            sheet_id = st.secrets["google"]["spreadsheet_id"]
        except KeyError as e:
            print(f"[sheets] Secret key 없음: {e} / 전체 keys: {list(st.secrets.keys())}")
            return False

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_info(dict(creds_info), scopes=scopes)
        gc = gspread.authorize(credentials)
        ws = gc.open_by_key(sheet_id).sheet1

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ws.append_row([timestamp, opp_number])
        return True

    except Exception as e:
        import traceback
        print(f"[sheets] Google Sheets 오류: {e}\n{traceback.format_exc()}")
        return False
