import os
from datetime import datetime

from dotenv import load_dotenv
from googleapiclient.discovery import build
from langchain.chat_models import init_chat_model

import smtplib
from email.mime.text import MIMEText

# Load .env once at module import
load_dotenv()


def load_credentials():
    """Load credentials from environment variables and validate them."""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME")

    # Validate credentials
    if not google_api_key or not spreadsheet_id or not sheet_name:
        raise RuntimeError("Missing GOOGLE_API_KEY, SPREADSHEET_ID OR SHEET_NAME in .env")

    return google_api_key, spreadsheet_id, sheet_name


def get_spreadsheet_data(google_api_key, spreadsheet_id, sheet_name):
    """Fetch spreadsheet data"""
    service = build('sheets', 'v4', developerKey=google_api_key)
    results = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()['values']
    return results


def get_current_row_count(sheet):
    """Count the total number of rows in the spreadsheet data"""
    return len(sheet)


def save_row_count(sheet_name, count):
    """Save the current row count for a specific sheet"""
    tracking_file = f"row_count_{sheet_name}.txt"

    # Read existing data
    try:
        with open(tracking_file, "w", encoding="utf-8") as file:
            file.write(str(count))
        # print(f"✔️ Saved count {count} to {tracking_file}")
    except OSError as exc:
        # Log but do not crash the whole flow
        print(f"⚠️ Failed to save row count: {exc}")


def get_last_row_count(sheet_name):
    """Get the last known row count for a specific sheet."""
    tracking_file = f"row_count_{sheet_name}.txt"
    try:
        with open(tracking_file, "r", encoding="utf-8") as file:
            count = file.read().strip()
            if not count:
                print(f"✔️ Empty tacking file for {sheet_name}, treating as 0.")
                return 0
            # print(f"✔️ Read from file: {count}")
            return int(count)
    except FileNotFoundError:
        print(f"✔️ No tracking file found for {sheet_name}.")
        return 0  # First time running, no previous count.
    except ValueError:
        print(f"✔️ Invalid data in file, resetting to 0.")
        return 0
    except OSError as exc:
        print(f"⚠️ Error reading tracking file: {exc}")
        return 0


def detect_new_rows(current_row_count, last_row_count):
    """Check if new rows were added and return the cound of new rows"""
    if current_row_count > last_row_count:
        new_row_count = current_row_count - last_row_count
        return True, new_row_count
    else:
        return False, 0
    

def get_new_rows(sheet, new_row_count):
    """Extract the new rows from the spreadsheet"""
    if new_row_count <= 0:
        return []
    # Get the last 'new_row_count' rows
    new_rows = sheet[-new_row_count:]
    return new_rows


def check_for_new_rows():
    """Check and display new rows"""
    # Load credentials and get data
    google_api_key, spreadsheet_id, sheet_name = load_credentials()
    rows = get_spreadsheet_data(google_api_key, spreadsheet_id, sheet_name)

    # Get counts
    current_row_count = get_current_row_count(rows)
    last_row_count = get_last_row_count(sheet_name)

    # check for new rows
    has_new_rows, new_row_count = detect_new_rows(current_row_count, last_row_count)

    if has_new_rows:
        print(f"{new_row_count} new row(s) detected!")

        # Get and display new rows
        new_rows = get_new_rows(rows, new_row_count)
        # print("\nNew rows added:")
        # for i, row in enumerate(new_rows, start=1):
        #     print(f"Row {i}: {row}")

        # Save the new count
        save_row_count(sheet_name, current_row_count)
        return new_rows
    else:
        print("✔️ No new rows added.")
        save_row_count(sheet_name, current_row_count)
        return []


def init_llm():
    """Initialize Gemini chat model via Langchain"""
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
    """Use LLM to summarize the newly added spreadsheet rows"""
    if not new_rows:
        return "No new rows to summarize."

    # Convert rows to readable text
    lines = []
    for row in new_rows:
        # Join cells with comma
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

    # Invoke model with prompt
    response = llm.invoke(prompt)
    return getattr(response, "content", str(response))


def load_email_credentials():
    """Load and validate email-related environment variables"""
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    # Validate credentials
    if not sender_email or not sender_password or not recipient_email:
        raise RuntimeError("Missing email credentials in .env file")

    return sender_email, sender_password, recipient_email


def send_email_summary(summary, new_row_count):
    """Send email with the AI summary of new rows"""
    try:
        sender_email, sender_password, recipient_email = load_email_credentials()
    except RuntimeError as exc:
        print(f"❌ {exc}")
        return False

    # Create email
    subject = f"Spreadsheet Update: {new_row_count} New Row(s) Added"

    # Email body
    body = (
        f"Hello,\n\n"
        f"Your Google Sheet has been updated with {new_row_count} new row(s).\n\n"
        f"=== AI Summary ===\n"
        f"{summary}\n\n"
        f"---\n"
        f"This is an automated notification from Spreadsheet AI Automation system.\n"
        f"Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
    )

    # Create message object
    message = MIMEText(body)
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Send email via Gmail SMTP
    try:
        # print("📧 Connecting to Gmail SMTP server...")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.starttls()  # Secure connection
            # print("🔐 Logging in...")
            server.login(sender_email, sender_password)
            print("📤 Sending email...")
            server.send_message(message)

        # print(f"✔️ Email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def main():
    check_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Starting spreadsheet check at {check_date_time}...")

    new_rows = check_for_new_rows()
    if not new_rows:
        print("\nNo new rows, nothing to summarize.")
        return

    llm = init_llm()
    summary = summarize_new_rows(llm, new_rows)
    #
    # print("\n=== AI SUMMARY OF NEW ROWS ===")
    # print(summary)

    # Send email with summary
    print("\n📧 Preparing to send email...")
    email_sent = send_email_summary(summary, len(new_rows))

    if email_sent:
        print("✔️ Email sent successfully!")
    else:
        print("⚠️ Email sending failed, but summary was generated.")


if __name__ == "__main__":
    main()
