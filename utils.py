import csv
import logging
import os
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)
CSV_FALLBACK = Path("registrations.csv")


def get_secret(key: str, fallback: str = "") -> str:
    """Read from st.secrets (Streamlit Cloud) with fallback to os.getenv (local)."""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, fallback)


def save_registration(data: dict) -> None:
    """
    Save a registration record.
    Primary:  Google Sheets (persistent on Streamlit Cloud).
    Fallback: local CSV (only reliable in local dev).
    """
    # ── Google Sheets ──────────────────────────────────────────────────────────
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        gc    = gspread.authorize(creds)
        sheet = gc.open(get_secret("SHEETS_DOCUMENT_NAME")).sheet1

        if not sheet.row_values(1):          # write header if empty
            sheet.append_row(list(data.keys()))
        sheet.append_row(list(data.values()))
        logger.info("Registration saved to Google Sheets.")
        return
    except Exception as exc:
        logger.warning("Google Sheets save failed (%s) — falling back to CSV.", exc)

    # ── CSV fallback ───────────────────────────────────────────────────────────
    try:
        file_exists = CSV_FALLBACK.exists()
        with CSV_FALLBACK.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        logger.info("Registration saved to CSV fallback.")
    except Exception as exc:
        logger.error("CSV fallback also failed: %s", exc)
