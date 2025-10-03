# API_log Default (FastAPI - Easy)
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uuid
import os
import uvicorn


class LogEntry(BaseModel):
    level: str  # ERROR, WARNING, INFO, DEBUG, SUCCESS (== Bot)
    message: str
    tags: Optional[List[str]] = []
    extra: Optional[Dict[str, Any]] = {}
    timestamp: Optional[str] = None


class LogResponse(BaseModel):
    logs: List[Dict[str, Any]]
    total: int
    since: Optional[str] = None


# Config
PROJECT_NAME = os.getenv('PROJECT_NAME', 'default_project')  # Name Project
DATABASE_PATH = f'{PROJECT_NAME}_logs.db'
MAX_LOGS_PER_REQUEST = 100

app = FastAPI(
    title=f"Logger API - {PROJECT_NAME}",
    description=f"API Managment Project: {PROJECT_NAME}",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_database():
    """Initialize the database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id TEXT PRIMARY KEY,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            tags TEXT,
            extra TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Indexing
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_level ON logs(level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON logs(created_at)')

    conn.commit()
    conn.close()



def get_logs(since: Optional[str] = None, level: Optional[str] = None,
             limit: int = MAX_LOGS_PER_REQUEST) -> LogResponse:
    """Get Logsا"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    query = "SELECT * FROM logs WHERE TRUE"
    params = []

    # Filter (DAte)
    if since:
        query += " AND timestamp > ?"
        params.append(since)

    # Filter (Level)
    if level:
        query += " AND level = ?"
        params.append(level.upper())

    # Order
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    logs = []
    for row in rows:
        log = {
            'id': row[0],
            'level': row[1],
            'message': row[2],
            'tags': json.loads(row[3]) if row[3] else [],
            'extra': json.loads(row[4]) if row[4] else {},
            'timestamp': row[5],
            'created_at': row[6]
        }
        logs.append(log)

    # Count All Logs
    count_query = "SELECT COUNT(*) FROM logs WHERE TRUE"
    count_params = []

    if since:
        count_query += " AND timestamp > ?"
        count_params.append(since)

    if level:
        count_query += " AND level = ?"
        count_params.append(level.upper())

    cursor.execute(count_query, count_params)
    total = cursor.fetchone()[0]

    conn.close()

    return LogResponse(logs=logs, total=total, since=since)


def cleanup_old_logs(days: int = 30, seconds: int = None):
    """Delete Older Logs"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    if seconds:
        cutoff_date = (datetime.now() - timedelta(seconds=seconds)).isoformat()
    else:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    cursor.execute("DELETE FROM logs WHERE created_at < ?", (cutoff_date,))

    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()

    return deleted_count


class LoggerAPI:
    def __init__(self):
        init_database()

    def add_log(self, log_entry: LogEntry):  # noqa
        """New Log"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        log_id = str(uuid.uuid4())
        timestamp = log_entry.timestamp or datetime.now().isoformat()
        tags_json = json.dumps(log_entry.tags) if log_entry.tags else "[]"
        extra_json = json.dumps(log_entry.extra) if log_entry.extra else "{}"

        cursor.execute('''
            INSERT INTO logs (id, level, message, tags, extra, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (log_id, log_entry.level.upper(), log_entry.message, tags_json, extra_json, timestamp))

        conn.commit()
        conn.close()

        return log_id


logger_api = LoggerAPI()


# Endpoints
@app.get("/", summary="Home")
async def root():
    return {
        "message": f"Logger API For Project {PROJECT_NAME}",
        "version": "1.0.0",
        "endpoints": {
            "Get Logs": "/logs",
            "Add Logs (POST)": "/logs",
            "Delete Older Logs": "/cleanup",
            "Stats Logs": "/stats"
        }
    }


@app.get("/logs", response_model=LogResponse, summary="Get Logs")
async def get_logs_route(
        since: Optional[str] = Query(None, description="Get Log Order By Date"),
        level: Optional[str] = Query(None, description="Get Log Order By Level"),
        limit: int = Query(50, description="Maximum Logs", le=MAX_LOGS_PER_REQUEST)
):
    """
    Get Logs With Filter

    - **since**: Start Date (ISO format)
    - **level**: Level Log (ERROR, WARNING, INFO, DEBUG, SUCCESS)
    - **limit**: Maximum Logs (Default: 50)
    """
    try:
        return get_logs(since=since, level=level, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching: {str(e)}")


@app.post("/logs", summary="Add New Logs")
async def add_log_route(log_entry: LogEntry):
    """
    Add New Logs

    - **level**: Level Logs (ERROR, WARNING, INFO, DEBUG, SUCCESS)
    - **message**: Text Message
    - **tags**: Custom Tags
    - **extra**: Extra Content (JSON)
    """
    try:
        log_id = logger_api.add_log(log_entry)
        return {
            "success": True,
            "log_id": log_id,
            "message": "Log added successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Log: {str(e)}")


@app.get("/stats", summary="Stats Logs")
async def get_stats_route():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM logs")
        total_logs = cursor.fetchone()[0]

        cursor.execute("""
            SELECT level, COUNT(*) as count 
            FROM logs 
            GROUP BY level 
            ORDER BY count DESC
        """)
        level_stats = dict(cursor.fetchall())

        # Stats 24 Hour
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM logs WHERE created_at > ?", (yesterday,))
        last_24h = cursor.fetchone()[0]

        # Stats 7 day
        last_week = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM logs WHERE created_at > ?", (last_week,))
        last_7days = cursor.fetchone()[0]

        # Last Log
        cursor.execute("SELECT timestamp FROM logs ORDER BY created_at DESC LIMIT 1")
        last_log_row = cursor.fetchone()
        last_log = last_log_row[0] if last_log_row else None

        conn.close()

        return {
            "project_name": PROJECT_NAME,
            "total_logs": total_logs,
            "level_stats": level_stats,
            "last_24h": last_24h,
            "last_7days": last_7days,
            "last_log_timestamp": last_log,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetch Stats: {str(e)}")


@app.post("/cleanup", summary="Clearing old logs")
async def cleanup_logs_route(
        days: int = Query(30, description="Delete logs older than this number of days."),
        seconds: int = Query(None, description="Delete logs older than this number of seconds."),):
    """Clear logs older than a specified number of days"""
    try:
        deleted_count = cleanup_old_logs(days, seconds)
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"{deleted_count} logs older than {str(seconds) + str(' seconds') if seconds else str(days) + str(' days')} were deleted."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in cleaning: {str(e)}")


@app.get("/health", summary="API health status")
async def health_check_route():
    """Checking API health status"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()

        return {
            "status": "healthy",
            "project": PROJECT_NAME,
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable:{str(e)}")


# Helper Class
class ProjectLogger:

    def __init__(self, project_name: str = PROJECT_NAME):
        self.project_name = project_name
        self.api = logger_api

    def log(self, level: str, message: str, tags: List[str] = None, **extra):
        log_entry = LogEntry(
            level=level,
            message=message,
            tags=tags or [],
            extra=extra
        )
        return self.api.add_log(log_entry)

    def error(self, message: str, tags: List[str] = None, **extra):
        return self.log("ERROR", message, tags, **extra)

    def warning(self, message: str, tags: List[str] = None, **extra):
        return self.log("WARNING", message, tags, **extra)

    def info(self, message: str, tags: List[str] = None, **extra):
        return self.log("INFO", message, tags, **extra)

    def debug(self, message: str, tags: List[str] = None, **extra):
        return self.log("DEBUG", message, tags, **extra)

    def success(self, message: str, tags: List[str] = None, **extra):
        return self.log("SUCCESS", message, tags, **extra)


project_logger = ProjectLogger()

if __name__ == "__main__":
    # Test
    print(f"Setting up the API for the project:{PROJECT_NAME}")
    print(f"Database path:{DATABASE_PATH}")

    # Tester Log
    project_logger.info("API launched", tags=["startup", "api"])
    project_logger.success("Database connected successfully.", tags=["database", "startup"])

    # Run Srrver
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8113,
        log_level="info"
    )