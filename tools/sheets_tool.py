import gspread
from crewai.tools import tool
from datetime import datetime

# Your specific Google Sheet ID
SHEET_ID = "1seXDWxtfqvuF6t0_OnWp_KysuOVlGERIVRdgLNwLWfU"

@tool
def sheets_tool(summary: str, url: str) -> str:
    """Appends the date, summary, URL data to a Google Sheet."""
    try:
        # 1. Log in using the bot's secret key
        gc = gspread.service_account(filename='tools/credentials.json')
        
        # 2. Open your specific spreadsheet
        sh = gc.open_by_key(SHEET_ID)
        
        # 3. Select the first tab (usually called "Sheet1")
        worksheet = sh.sheet1

        date = datetime.now().strftime("%Y-%m-%d")
        
        # 4. Add a new row with the summary text
        worksheet.append_row([date, summary, url])
        
        return "Successfully saved the summary to Google Sheets!"
    except Exception as e:
        return f"Failed to save to Google Sheets. Error: {str(e)}"