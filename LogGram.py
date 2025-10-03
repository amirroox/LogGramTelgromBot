# LogGram.py
import asyncio
import sqlite3
import json
from datetime import datetime
from telethon import TelegramClient, events, Button
import aiohttp
import logging
import config

# Main Config
API_ID = config.API_ID  # From my.telegram.org
API_HASH = config.API_HASH
BOT_TOKEN = config.BOT_TOKEN
ADMIN_USER_ID = config.ADMIN_USER_ID  # Your Admin ID

# Logging Option
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initial DataBase
def init_database():
    """Main DB"""
    conn = sqlite3.connect('logger_bot.db')
    cursor = conn.cursor()

    # Projects
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            api_url TEXT NOT NULL,
            chat_id INTEGER NOT NULL,
            tags TEXT,
            last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sent_logs (
            id INTEGER PRIMARY KEY,
            project_name TEXT,
            log_id TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(project_name, log_id)
        )
    ''')

    conn.commit()
    conn.close()
    logger.info("Database initialized")


async def fetch_logs_from_project(project_name: str, api_url: str, last_check: str):
    """Get Logs From Project (API)"""
    try:
        params = {
            'since': last_check,
            'format': 'json'
        }

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            print(f"{api_url}/logs")
            async with session.get(f"{api_url}/logs", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('logs', [])
                else:
                    logger.error(f"Error Fetch Project: {project_name}: HTTP {response.status}")
                    return []

    except asyncio.TimeoutError:
        logger.error(f"TiemOut Connection Project: {project_name}")
        return []
    except Exception as e:
        logger.error(f"Error Get Logs Project: {project_name}: {str(e)}")
        return []


async def format_log_message(project_name: str, log: dict):
    """Formater"""
    level = log.get('level', 'INFO').upper()
    message = log.get('message', '')
    timestamp = log.get('timestamp', '')
    tags = log.get('tags', [])

    # Color Emoji
    emoji_map = {
        'ERROR': '🔴',
        'CRITICAL': '💥',
        'WARNING': '🟡',
        'INFO': '🔵',
        'DEBUG': '🟣',
        'SUCCESS': '🟢'
    }
    emoji = emoji_map.get(level, '📝')

    text = f"{emoji} **{project_name}** - {level}\n\n"
    text += f"📅 **Date:** `{timestamp}`\n"

    if tags:
        text += f"🏷 **Tags:** {', '.join(tags)}\n"

    text += f"\n💬 **Message:**\n```\n{message}\n```"

    if 'extra' in log:
        text += f"\n\n📋 **Extra Content:**\n```json\n{json.dumps(log['extra'], indent=2, ensure_ascii=False)}\n```"

    return text


class TelegramLoggerBot:
    def __init__(self):
        self.client = TelegramClient('logger_bot', API_ID, API_HASH)
        init_database()
        self.projects = {}
        self.load_projects()
        self.is_running = False

    def load_projects(self):
        """Loading Projects"""
        conn = sqlite3.connect('logger_bot.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE active = 1')

        self.projects = {}
        for row in cursor.fetchall():
            self.projects[row[1]] = {
                'id': row[0],
                'api_url': row[2],
                'chat_id': row[3],
                'tags': row[4].split(',') if row[4] else [],
                'last_check': row[5]
            }
        conn.close()
        logger.info(f"{len(self.projects)} Loaded Projects")

    async def add_project(self, name: str, api_url: str, chat_id: int, tags: str = ""):
        """Add New Project"""
        conn = sqlite3.connect('logger_bot.db')
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO projects (name, api_url, chat_id, tags)
                VALUES (?, ?, ?, ?)
            ''', (name, api_url, chat_id, tags))
            conn.commit()

            project_id = cursor.lastrowid
            self.projects[name] = {
                'id': project_id,
                'api_url': api_url,
                'chat_id': chat_id,
                'tags': tags.split(',') if tags else [],
                'last_check': datetime.now().isoformat()
            }

            conn.close()
            return True, f"پروژه '{name}' با موفقیت اضافه شد ✅"

        except sqlite3.IntegrityError:
            conn.close()
            return False, f"پروژه '{name}' قبلاً وجود دارد ❌"
        except Exception as e:
            conn.close()
            return False, f"خطا در اضافه کردن پروژه: {str(e)} ❌"

    async def remove_project(self, name: str):
        """Delete Project"""
        if name not in self.projects:
            return False, f"پروژه '{name}' یافت نشد ❌"

        conn = sqlite3.connect('logger_bot.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE projects SET active = 0 WHERE name = ?', (name,))
        conn.commit()
        conn.close()

        del self.projects[name]
        return True, f"پروژه '{name}' حذف شد ✅"

    async def list_projects(self):
        """List Projects"""
        if not self.projects:
            return "هیچ پروژه‌ای ثبت نشده است 📝"

        text = "📋 **لیست پروژه‌ها:**\n\n"
        for name, info in self.projects.items():
            status = "🟢 فعال" if self.is_running else "🟡 متوقف"
            text += f"**{name}**\n"
            text += f"├ وضعیت: {status}\n"
            text += f"├ API: `{info['api_url']}`\n"
            text += f"├ چت: `{info['chat_id']}`\n"
            text += f"├ تگ‌ها: {', '.join(info['tags']) if info['tags'] else 'ندارد'}\n"
            text += f"└ آخرین چک: {info['last_check']}\n\n"

        return text

    async def send_log_to_chat(self, chat_id: int, project_name: str, log: dict):
        """Send Logs In Bot"""
        try:
            message = await format_log_message(project_name, log)
            await self.client.send_message(chat_id, message, parse_mode='markdown')

            log_id = log.get('id', f"{project_name}_{log.get('timestamp', '')}")
            conn = sqlite3.connect('logger_bot.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO sent_logs (project_name, log_id)
                VALUES (?, ?)
            ''', (project_name, log_id))
            conn.commit()
            conn.close()

            return True
        except Exception as e:
            logger.error(f"Error In Send Logs {project_name}: {str(e)}")
            return False

    async def check_all_projects(self):
        """Check All Projects (All Logs)"""
        if not self.projects:
            return

        logger.info("Checking All Projects ...")

        for project_name, info in self.projects.items():
            try:
                logs = await fetch_logs_from_project(
                    project_name,
                    info['api_url'],
                    info['last_check']
                )

                if logs:
                    logger.info(f"{len(logs)} New Logs {project_name} Found.")

                    for log in logs:
                        await self.send_log_to_chat(info['chat_id'], project_name, log)
                        await asyncio.sleep(1)  # TimeOut Spammer

                    # Set Last Cheking
                    self.update_last_check(project_name)

            except Exception as e:
                logger.error(f"Error Checking Project: {project_name}: {str(e)}")
                await asyncio.sleep(2)

    def update_last_check(self, project_name: str):
        """Update Last Check (Setter)"""
        now = datetime.now().isoformat()
        self.projects[project_name]['last_check'] = now

        conn = sqlite3.connect('logger_bot.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE projects SET last_check = ? WHERE name = ?
        ''', (now, project_name))
        conn.commit()
        conn.close()

    async def start_monitoring(self):
        """Monotoring (Start)"""
        if not self.projects:
            return False, "بدون پروژه چیو میخوای مانیتور کنی؟"
        if self.is_running:
            return False, "مانیتورینگ قبلاً شروع شده است! 🔄"

        self.is_running = True

        asyncio.create_task(self.monitoring_loop())
        return True, "مانیتورینگ شروع شد! ✅"

    async def stop_monitoring(self):
        """Monotoring (End)"""
        if not self.is_running:
            return False, "مانیتورینگ از قبل متوقف است! ⏹"

        self.is_running = False
        return True, "مانیتورینگ متوقف شد! ⏹"

    async def monitoring_loop(self):
        """Monotoring (Main Loop)"""
        while self.is_running:
            try:
                await self.check_all_projects()
                # Cron 1 Hour
                await asyncio.sleep(3600)  # 1 hour
            except Exception as e:
                logger.error(f"Error In Monitoring: {str(e)}")
                await asyncio.sleep(60)

    def setup_handlers(self):
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            if event.sender_id != ADMIN_USER_ID:
                await event.respond("شما رو نمیشناسم! ❌")
                return

            buttons = [
                [Button.inline("📝 افزودن پروژه", b"add_project")],
                [Button.inline("📋 لیست پروژه‌ها", b"list_projects")],
                [Button.inline("▶️ شروع مانیتورینگ", b"start_monitoring")],
                [Button.inline("⏹ توقف مانیتورینگ", b"stop_monitoring")],
                [Button.inline("🗑 حذف پروژه", b"remove_project")],
                [Button.inline("راهنما", b"help")]
            ]

            await event.respond(
                "🤖 **ربات لاگینگ تلگرام** خوش آمدید!\n\n"
                "برای شروع یکی از گزینه‌های زیر را انتخاب کنید:",
                buttons=buttons
            )

        @self.client.on(events.CallbackQuery)  # noqa
        async def callback_handler(event):
            if event.sender_id != ADMIN_USER_ID:
                await event.answer("شما؟", alert=True)
                return

            data = event.data.decode()

            if data == "add_project":
                await event.respond(
                    "📝 **افزودن پروژه جدید**\n\n"
                    "Format:\n `/add Project_name API_URL CHAT_ID [TAGS]`\n\n"
                    "Example:\n"
                    "`/add RooxProject http://192.168.1.100:8000 -1001234567890 error,warning`"
                )

            elif data == "list_projects":
                projects_list = await self.list_projects()
                await event.respond(projects_list)

            elif data == "start_monitoring":
                success, message = await self.start_monitoring()
                await event.respond(message)

            elif data == "stop_monitoring":
                success, message = await self.stop_monitoring()
                await event.respond(message)

            elif data == "remove_project":
                if not self.projects:
                    await event.respond("هیچ پروژه‌ای برای حذف وجود ندارد! 📝")
                else:
                    projects_text = "\n".join([f"• {name}" for name in self.projects.keys()])
                    await event.respond(
                        f"🗑 **حذف پروژه**\n\n"
                        f"پروژه‌های موجود:\n{projects_text}\n\n"
                        f"فرمت: `/remove نام_پروژه`\n\n"
                        f"مثال: `/remove myproject`"
                    )

            elif data == "help":
                help_text = """
ℹ️ **راهنمای استفاده**

**دستورات:**
• `/add نام API_URL CHAT_ID [TAGS]` - افزودن پروژه
• `/remove نام_پروژه` - حذف پروژه  
• `/list` - نمایش پروژه‌ها
• `/start_monitor` - شروع مانیتورینگ
• `/stop_monitor` - توقف مانیتورینگ
• `/status` - وضعیت ربات

**نکات:**
- ربات هر ساعت یکبار پروژه‌ها را چک می‌کند
- API باید endpoint `/logs` داشته باشد
- فرمت پاسخ API باید JSON باشد
- CHAT_ID میتواند گروه یا کانال باشد
                """
                await event.respond(help_text)

            await event.answer()

        @self.client.on(events.NewMessage(pattern=r'/add (.+)'))
        async def add_project_handler(event):
            if event.sender_id != ADMIN_USER_ID:
                return

            try:
                args = event.pattern_match.group(1).split()
                if len(args) < 3:
                    await event.respond("❌ فرمت نادرست!\n\n`/add نام_پروژه API_URL CHAT_ID [TAGS]`")
                    return

                name = args[0]
                api_url = args[1]
                chat_id = int(args[2])
                tags = args[3] if len(args) > 3 else ""

                success, message = await self.add_project(name, api_url, chat_id, tags)
                await event.respond(message)

            except ValueError:
                await event.respond("❌ CHAT_ID باید عدد باشد!")
            except Exception as e:
                await event.respond(f"❌ خطا: {str(e)}")

        @self.client.on(events.NewMessage(pattern=r'/remove (.+)'))
        async def remove_project_handler(event):
            if event.sender_id != ADMIN_USER_ID:
                return

            name = event.pattern_match.group(1).strip()
            success, message = await self.remove_project(name)
            await event.respond(message)

        @self.client.on(events.NewMessage(pattern='/list'))
        async def list_handler(event):
            if event.sender_id != ADMIN_USER_ID:
                return

            projects_list = await self.list_projects()
            await event.respond(projects_list)

        @self.client.on(events.NewMessage(pattern='/start_monitor'))
        async def start_monitor_handler(event):
            if event.sender_id != ADMIN_USER_ID:
                return

            success, message = await self.start_monitoring()
            await event.respond(message)

        @self.client.on(events.NewMessage(pattern='/stop_monitor'))
        async def stop_monitor_handler(event):
            if event.sender_id != ADMIN_USER_ID:
                return

            success, message = await self.stop_monitoring()
            await event.respond(message)

        @self.client.on(events.NewMessage(pattern='/status'))
        async def status_handler(event):
            if event.sender_id != ADMIN_USER_ID:
                return

            status = "🟢 فعال" if self.is_running else "🔴 غیرفعال"
            projects_count = len(self.projects)

            await event.respond(
                f"📊 **وضعیت ربات**\n\n"
                f"• مانیتورینگ: {status}\n"
                f"• تعداد پروژه‌ها: {projects_count}\n"
                f"• آخرین آپدیت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

    async def run(self):
        await self.client.start(bot_token=BOT_TOKEN)
        self.setup_handlers()
        logger.info("Running Bot Tel")

        # Send Notif
        try:
            await self.client.send_message(
                ADMIN_USER_ID,
                "🤖 **ربات لاگینگ راه‌اندازی شد!**\n\n"
                "برای شروع /start را بزنید."
            )
        except Exception as e:
            logger.error(e)
            pass

        await self.client.run_until_disconnected()


# Running
async def main():
    bot = TelegramLoggerBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())