# Spreadsheet AI Automation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent automation tool that monitors Google Sheets for new entries, generates AI-powered summaries using Google Gemini, and sends email notifications automatically.

## 🌟 Features

- **Real-time Monitoring**: Automatically detects new rows added to your Google Sheet
- **AI-Powered Summaries**: Uses Google Gemini 2.5 Flash via LangChain to generate concise, email-ready summaries
- **Email Notifications**: Sends automated email alerts with summaries of new entries
- **Persistent Tracking**: Maintains state across runs to detect only new additions
- **Production-Ready**: Robust error handling and validation

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Cloud account with Sheets API enabled
- Gmail account with App Password enabled
- Google API key for Gemini

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vinodvv/Spreadsheet-AI-Automation.git
   cd Spreadsheet-AI-Automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Google Sheets Configuration
   GOOGLE_API_KEY=your_google_api_key_here
   SPREADSHEET_ID=your_spreadsheet_id_here
   SHEET_NAME=Sheet1
   
   # Email Configuration
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password-here
   RECIPIENT_EMAIL=recipient@example.com
   ```

### Getting Your Credentials

#### 1. Google API Key
- Go to [Google Cloud](https://console.cloud.google.com/apis/credentials)
- Create a new API key
- Copy the key to your `.env` file

#### 2. Spreadsheet ID
- Open your Google Sheet
- Copy the ID from the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

#### 3. Gmail App Password
- Go to your [Google Account](https://myaccount.google.com/)
- Navigate to Security → 2-Step Verification → App passwords
- Generate a new app password
- Copy the 16-character password to your `.env` file

## 📖 Usage

### Basic Usage

Run the script manually:
```bash
python send_ai_summary.py
```

### Automated Scheduling

#### Using Cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add this line to run every hour
0 * * * * cd /path/to/Spreadsheet-AI-Automation && /usr/bin/python3 send_ai_summary.py >> logs/cron.log 2>&1
```

#### Using Task Scheduler (Windows)
1. Open Task Scheduler
2. Create a new task
3. Set trigger (e.g., every hour)
4. Set action: `python.exe` with argument `C:\path\to\send_ai_summary.py`

#### Using GitHub Actions
See the [workflows](.github/workflows) directory for examples.

## 🏗️ Project Structure

```
Spreadsheet_AI_Automation/
├── send_ai_summary.py      # Main application script
├── .env                    # Environment variables (create this)
├── .env.example            # Example environment file
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── LICENSE                 # MIT License
└── row_count_*.txt         # Auto-generated tracking files
```

## 🔧 Configuration

### Customizing the AI Prompt

Edit the `summarize_new_rows()` function in `send_ai_summary.py`:

```python
prompt = (
    "You are an assistant that writes short email-ready summaries of new entries"
    "in a Google Sheet.\n\n"
    "Here are the new rows:\n"
    f"{rows_text}\n\n"
    "Write a concise summary (3-5 bullet points) highlighting key information."
    "Do not invent data."
)
```

### Adjusting LLM Parameters

Modify the `init_llm()` function:

```python
llm = init_chat_model(
    "gemini-2.5-flash",
    model_provider="google-genai",
    temperature=0.3,  # Adjust creativity (0.0 - 1.0)
)
```

## 📋 Requirements

```txt
google-api-python-client>=2.0.0
langchain>=0.1.0
langchain-google-genai>=0.0.5
python-dotenv>=1.0.0
```

## 🛠️ Troubleshooting

### Common Issues

**"Missing credentials in .env"**
- Ensure all required environment variables are set in your `.env` file

**"Failed to send email: authentication failed"**
- Verify you're using an App Password, not your regular Gmail password
- Ensure 2-Factor Authentication is enabled on your Google account

**"Google Sheets API error"**
- Check that your `SPREADSHEET_ID` is correct
- Ensure the spreadsheet is accessible (publicly shared or accessible via API key)
- Verify that the `SHEET_NAME` matches exactly (case-sensitive)

**Email not sending**
- Check your Gmail security settings
- Verify the SMTP settings (smtp.gmail.com:587)
- Ensure your internet connection is stable

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini](https://deepmind.google/technologies/gemini/) for AI capabilities
- [LangChain](https://www.langchain.com/) for LLM integration
- [Google Sheets API](https://developers.google.com/sheets/api) for spreadsheet access

## 📧 Contact

Vinod VV - [@vinodvv](https://github.com/vinodvv)

Project Link: [https://github.com/vinodvv/Spreadsheet-AI-Automation](https://github.com/vinodvv/Spreadsheet-AI-Automation)

---

**Note**: This tool is designed for personal use and small-scale automation. For production environments with high-frequency updates, consider implementing rate limiting and more sophisticated error handling.