# LogGram - Telegram Logger Bot 🤖

A professional logging system that sends your project logs directly to Telegram. Monitor your applications in real-time through a simple Telegram bot.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Examples](#examples)

---

## 🎯 Overview

LogGram consists of three main components:

1. **Logger API** (`logger_api.py`) - A FastAPI-based REST API that stores and manages logs
2. **Telegram Bot** (`LogGram.py`) - A Telegram bot that fetches logs from your projects and sends them to designated chats
3. **Client Library** (`ExampleUse.py`) - Example implementation showing how to integrate the logger into your projects

---

## ✨ Features

- 📊 Real-time log monitoring via Telegram
- 🎨 Color-coded log levels (ERROR, WARNING, INFO, DEBUG, SUCCESS)
- 🏷️ Custom tags for organizing logs
- 📈 Statistics and analytics
- 🔍 Filter logs by date, level, and tags
- 🗄️ SQLite database for reliable storage
- 🚀 Easy integration with existing projects
- ⏰ Automatic log cleanup
- 🔒 Admin-only bot access

---

## 📁 Project Structure

```
LogGram/
├── logger_api.py      # FastAPI logging API
├── LogGram.py         # Telegram bot
├── ExampleUse.py      # Usage example
├── config.py          # Configuration file
└── README.md          # This file
```

---

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install fastapi uvicorn telethon aiohttp psutil requests
```

### 2. Get Telegram Credentials

Visit [my.telegram.org](https://my.telegram.org) and create an application to get:
- `API_ID`
- `API_HASH`

### 3. Create a Bot

Talk to [@BotFather](https://t.me/BotFather) on Telegram to create a bot and get:
- `BOT_TOKEN`

### 4. Get Your User ID

Talk to [@userinfobot](https://t.me/userinfobot) to get your:
- `ADMIN_USER_ID`

---

## ⚙️ Configuration

Create a `config.py` file:

```python
API_ID = 12345678  # From my.telegram.org
API_HASH = "your_api_hash_here"
BOT_TOKEN = "your_bot_token_here"
ADMIN_USER_ID = 123456789  # Your Telegram user ID
```

---

## 📖 Usage

### Step 1: Start the Logger API

Run the API server for your project:

```bash
# Set your project name (optional)
export PROJECT_NAME="my_project"

# Run the API
python logger_api.py
```

The API will start on `http://127.0.0.1:8113`

### Step 2: Start the Telegram Bot

In a separate terminal:

```bash
python LogGram.py
```

### Step 3: Configure the Bot

1. Send `/start` to your bot
2. Click "📝 Add Project"
3. Use the command:
   ```
   /add ProjectName http://YOUR_IP:8113 YOUR_CHAT_ID error,warning
   ```
   
   Example:
   ```
   /add MyApp http://192.168.1.100:8113 -1001234567890 error,warning
   ```

4. Start monitoring:
   ```
   /start_monitor
   ```

### Step 4: Integrate into Your Project

Copy `logger_api.py` to your project and use it:

```python
from logger_api import project_logger

# Log messages
project_logger.info("Application started")
project_logger.error("Database connection failed", tags=["database"])
project_logger.success("User registered successfully", user_id=123)
```

---

## 🔌 API Endpoints

### GET `/logs`
Get logs with filtering options

**Parameters:**
- `since` - Get logs after this timestamp (ISO format)
- `level` - Filter by log level (ERROR, WARNING, INFO, DEBUG, SUCCESS)
- `limit` - Maximum number of logs (default: 50, max: 100)

**Example:**
```bash
curl "http://localhost:8113/logs?level=ERROR&limit=10"
```

### POST `/logs`
Add a new log entry

**Body:**
```json
{
  "level": "ERROR",
  "message": "Something went wrong",
  "tags": ["database", "critical"],
  "extra": {
    "user_id": 123,
    "error_code": "DB_001"
  }
}
```

### GET `/stats`
Get logging statistics

### POST `/cleanup`
Delete old logs

**Parameters:**
- `days` - Delete logs older than X days (default: 30)
- `seconds` - Delete logs older than X seconds

### GET `/health`
Check API health status

---

## 💡 Examples

### Basic Logging

```python
from logger_api import project_logger

# Simple log
project_logger.info("Application started")

# Log with tags
project_logger.error("Connection failed", tags=["network", "critical"])

# Log with extra data
project_logger.warning(
    "High memory usage detected",
    tags=["system", "memory"],
    memory_percent=85.2,
    threshold=80
)
```

### Error Handling

```python
try:
    # Your code here
    result = risky_operation()
except Exception as e:
    project_logger.error(
        f"Operation failed: {str(e)}",
        tags=["error", "operation"],
        error_type=type(e).__name__,
        traceback=str(e)
    )
```

### System Monitoring

```python
import psutil

cpu_percent = psutil.cpu_percent(interval=1)

if cpu_percent > 80:
    project_logger.warning(
        f"High CPU usage: {cpu_percent}%",
        tags=["system", "cpu"],
        cpu_percent=cpu_percent,
        threshold=80
    )
```

### Async Operations

```python
async def async_task():
    try:
        project_logger.info("Starting async task", tags=["async"])
        
        # Your async code
        await some_async_operation()
        
        project_logger.success("Async task completed", tags=["async"])
    except Exception as e:
        project_logger.error(
            f"Async task failed: {str(e)}",
            tags=["async", "error"]
        )
```

---

## 🤖 Bot Commands

- `/start` - Show main menu
- `/add <name> <api_url> <chat_id> [tags]` - Add a new project
- `/remove <name>` - Remove a project
- `/list` - List all projects
- `/start_monitor` - Start monitoring all projects
- `/stop_monitor` - Stop monitoring
- `/status` - Show bot status

---

## 📊 Log Levels

- 🔴 **ERROR** - Application errors and exceptions
- 🟡 **WARNING** - Warning messages and potential issues
- 🔵 **INFO** - General information messages
- 🟣 **DEBUG** - Debug information for development
- 🟢 **SUCCESS** - Successful operations

---

## 🔒 Security Notes

- Only the admin user (configured in `config.py`) can control the bot
- Keep your `config.py` file private and never commit it to version control
- Use environment variables for sensitive data in production
- Consider using HTTPS for the API in production environments

---

## 🐛 Troubleshooting

### Bot doesn't respond
- Check if `ADMIN_USER_ID` is correct
- Verify bot token is valid
- Ensure bot is running without errors

### Logs not appearing
- Verify API URL is accessible
- Check if monitoring is started (`/start_monitor`)
- Confirm chat_id is correct (use negative numbers for groups/channels)

### Database issues
- Check write permissions for the directory
- Verify SQLite is installed correctly
- Try deleting `.db` files and restarting

---

## 📝 License

This project is open source and available for personal and commercial use.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Made with ❤️ for better logging**