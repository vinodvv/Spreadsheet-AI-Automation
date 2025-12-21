import os
from googleapiclient.discovery import build
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from datetime import datetime


def load_credentials():
    """Load credentials from .env file"""
    load_dotenv()

    google_api_key = os.getenv("GOOGLE_API_KEY")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME")
    return google_api_key, spreadsheet_id, sheet_name


def get_spreadsheet_data(google_api_key, spreadsheet_id, sheet_name):
    """Fetch spreadsheet data"""
    service = build('sheets', 'v4', developerKey=google_api_key)
    results = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()['values']
    return results


def get_current_row_count(data):
    """Count the total number of rows in the spreadsheet data"""
    return len(data)


def save_row_count(sheet_name, count):
    """Save the current row count for a specific sheet"""
    tracking_file = f"row_count_{sheet_name}.txt"
    # Read existing data
    try:
        with open(tracking_file, "w") as file:
            file.write(str(count))
        print(f"✔️ Saved count {count} to {tracking_file}")
    except FileNotFoundError:
        pass


def get_last_row_count(sheet_name):
    """Get the last known row count for a specific sheet"""
    tracking_file = f"row_count_{sheet_name}.txt"
    try:
        with open(tracking_file, "r") as file:
            count = file.read().strip()
            # print(f"✔️ Read from file: {count}")
            return int(count)
    except FileNotFoundError:
        print(f"✔️ No tracking file found for {sheet_name}")
        return 0  # First time running, no previous count.
    except ValueError:
        print(f"✔️ Invalid data in file, resetting to 0")
        return 0


def detect_new_rows(current_row_count, last_row_count):
    """Check if new rows were added and return the count of new rows"""
    if current_row_count > last_row_count:
        new_row_count = current_row_count - last_row_count
        return True, new_row_count
    else:
        return False, 0


def get_new_rows(data, new_row_count):
    """Extract the new rows from the data"""
    if new_row_count > 0:
        # Get the last 'new_row_count' rows
        new_rows = data[-new_row_count:]
        return new_rows
    else:
        return []


def check_for_new_rows():
    """Main function to check for and display new rows"""
    # Load credentials and get data
    google_api_key, spreadsheet_id, sheet_name = load_credentials()
    rows = (get_spreadsheet_data(google_api_key, spreadsheet_id, sheet_name))
    # print("ALL ROWS:")
    # for i, row in enumerate(rows, 1):
    #     print(f"Row {i}: {row}")
    # print(f"{len(rows)} rows total.")

    # Get counts
    current_row_count = get_current_row_count(rows)
    last_row_count = get_last_row_count(sheet_name)

    # print(f"Sheet: {sheet_name}")
    # print(f"Last row count: {last_row_count}")
    # print(f"Current row count: {current_row_count}")

    # Check for new rows
    has_new_rows, new_row_count = detect_new_rows(current_row_count, last_row_count)

    if has_new_rows:
        print(f"{new_row_count} new row(s) detected!")

        # Get and display new rows
        news_rows = get_new_rows(rows, new_row_count)
        print("\nNew rows added:")
        for i, row in enumerate(news_rows, start=1):
            print(f"Row {i}: {row}")

        # Save the new count
        save_row_count(sheet_name, current_row_count)
        return news_rows
    else:
        print("✔️ No new rows added.")
        save_row_count(sheet_name, current_row_count)
        return []


def init_llm():
    """Initialize Gemini chat model via LangChain"""
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY in .env")

    llm = init_chat_model(
        "gemini-2.5-flash",
        model_provider="google-genai",
        temperature=0.3,
    )
    return llm


def summarize_new_rows(llm, new_rows):
    """Use LLM to summarize the newly added spreadsheet rows."""
    if not new_rows:
        return "No new rows to summarize."

    # Convert rows to readable text
    lines = []
    for row in new_rows:
        # join cells with comma; adjust as needed for your schema
        line = ", ".join(str(cell) for cell in row)
        lines.append(f"- {line}")
    rows_text = "\n".join(lines)

    prompt = (
        "You are an assistant that writes short email-ready summaries of new entries"
        "in a Google Sheet.\n\n"
        "Here are the new rows:\n"
        f"{rows_text}\n\n"
        "Write a concise summary (3-5 bullet points) highlighting key information."
        "Do not invent data."
    )

    # For chat models, 'invoke' can take a plain string message.
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    # # Temporary quick test
    # llm = init_llm()
    # response = llm.invoke("Summarize this in one sentence: I am testing my Gemini + LangChain setup.")
    # print("LLM reply:", response.content)

    check_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Starting spreadsheet check at {check_date_time}.")
    new_rows = check_for_new_rows()

    if new_rows:
        llm = init_llm()
        summary = summarize_new_rows(llm, new_rows)
        print("\n=== AI SUMMARY OF NEW ROWS ===")
        print(summary)
    else:
        print("\nNo new rows, nothing to summarize.")
