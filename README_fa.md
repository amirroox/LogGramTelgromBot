[Engilsh Version](./README.md)

<div dir="rtl">

🤖 LogGram - سیستم لاگینگ تلگرامی
=================================

یک سیستم لاگینگ حرفه‌ای که لاگ‌های پروژه شما را مستقیماً به تلگرام ارسال می‌کند. برنامه‌های خود را به صورت Real-Time از طریق یک ربات تلگرام ساده مانیتور کنید.

📋 فهرست مطالب
--------------

*   [معرفی](#overview)
*   [امکانات](#features)
*   [ساختار پروژه](#structure)
*   [نصب و راه‌اندازی](#install)
*   [تنظیمات](#config)
*   [نحوه استفاده](#usage)
*   [API Endpoints](#api)
*   [مثال‌های کاربردی](#examples)

* * *

<div id="overview" dir="rtl">

🎯 معرفی
--------

خب LogGram از سه بخش اصلی تشکیل شده است:

1.  فایل **Logger API** (`logger_api.py`) - یک REST API مبتنی بر FastAPI که لاگ‌ها را ذخیره و مدیریت می‌کند
2.  فایل **Telegram Bot** (`LogGram.py`) - یک ربات تلگرام که لاگ‌ها را از پروژه‌های شما دریافت کرده و به چت‌های تعیین شده ارسال می‌کند
3.  **کتابخانه کلاینت** (`ExampleUse.py`) - نمونه پیاده‌سازی که نحوه یکپارچه‌سازی logger در پروژه‌ها را نشان می‌دهد

* * *

</div>

<div id="features">

✨ امکانات
---------

*   📊 مانیتورینگ لاگ‌ها به صورت Real-time از طریق تلگرام
*   🎨 سطوح لاگ رنگی (ERROR, WARNING, INFO, DEBUG, SUCCESS)
*   🏷️ تگ‌های سفارشی برای سازماندهی لاگ‌ها
*   📈 آمار و تحلیل‌های دقیق
*   🔍 فیلتر لاگ‌ها بر اساس تاریخ، سطح و تگ
*   🗄️ پایگاه داده SQLite برای ذخیره‌سازی قابل اعتماد
*   🚀 یکپارچه‌سازی آسان با پروژه‌های موجود
*   ⏰ پاکسازی خودکار لاگ‌های قدیمی
*   🔒 دسترسی فقط برای ادمین

* * *

</div>

<div id="structure">

📁 ساختار پروژه
---------------

<div dir="ltr">

    LogGram/
    ├── logger_api.py      # API لاگینگ FastAPI
    ├── LogGram.py         # ربات تلگرام
    ├── ExampleUse.py      # مثال استفاده
    ├── config.py          # فایل تنظیمات
    └── README.md          # این فایل
    

* * *

</div>

</div>

<div id="install">

🚀 نصب و راه‌اندازی
-------------------

### مرحله 1: نصب وابستگی‌ها

<div dir="ltr">

    pip install fastapi uvicorn telethon aiohttp psutil requests
    
</div>

### مرحله 2: دریافت اطلاعات تلگرام

به سایت [my.telegram.org](https://my.telegram.org) بروید و یک اپلیکیشن بسازید تا این موارد را دریافت کنید:

*   `API_ID`
*   `API_HASH`

### مرحله 3: ساخت ربات

با [@BotFather](https://t.me/BotFather) در تلگرام صحبت کنید و یک ربات بسازید تا دریافت کنید:

*   `BOT_TOKEN`

### مرحله 4: دریافت User ID

با [@userinfobot](https://t.me/userinfobot) صحبت کنید تا دریافت کنید:

*   `ADMIN_USER_ID`

* * *

<div id="config">

⚙️ تنظیمات
----------

یک فایل `config.py` بسازید:

<div dir="ltr">

    API_ID = 12345678  # از my.telegram.org
    API_HASH = "your_api_hash_here"
    BOT_TOKEN = "your_bot_token_here"
    ADMIN_USER_ID = 123456789  # شناسه کاربری تلگرام شما
    
</div>

</div>

* * *

</div>

<div id="usage">

📖 نحوه استفاده
---------------

### گام 1: راه‌اندازی Logger API

سرور API را برای پروژه خود اجرا کنید:

<div dir="ltr">

    # تنظیم نام پروژه (اختیاری)
    export PROJECT_NAME="my_project"
    
    # اجرای API
    python logger_api.py
    
</div>

API روی آدرس `http://127.0.0.1:8113` اجرا می‌شود

### گام 2: راه‌اندازی ربات تلگرام

در یک ترمینال جدید:

<div dir="ltr">

    python LogGram.py
    
</div>

### گام 3: تنظیم ربات

1.  دستور `/start` را به ربات خود ارسال کنید
2.  روی دکمه "📝 افزودن پروژه" کلیک کنید
3.  از این دستور استفاده کنید:
    
<div dir="ltr">

    /add ProjectName http://YOUR_IP:8113 YOUR_CHAT_ID error,warning
        
</div>
    

**💡 نکته:** برای دریافت `chat_id` گروه یا کانال، می‌توانید از ربات [@userinfobot](https://t.me/userinfobot) استفاده کنید. برای گروه‌ها و کانال‌ها عدد منفی است (مثال: `-1001234567890`)

**مثال:**

<div dir="ltr">

    /add MyApp http://192.168.1.100:8113 -1001234567890 error,warning
    
</div>

4.  شروع مانیتورینگ:
    
<div dir="ltr">

    /start_monitor
        
</div>
    

### گام 4: یکپارچه‌سازی در پروژه

فایل `logger_api.py` را در پروژه خود کپی کنید و از آن استفاده کنید:

<div dir="ltr">

    from logger_api import project_logger
    
    # ثبت لاگ‌ها
    project_logger.info("برنامه شروع شد")
    project_logger.error("اتصال به دیتابیس ناموفق بود", tags=["database"])
    project_logger.success("کاربر با موفقیت ثبت نام کرد", user_id=123)

* * *

</div>

</div>

<div id="api">

🔌 API Endpoints
----------------

### GET `/logs`

دریافت لاگ‌ها با امکان فیلترینگ

**پارامترها:**

*   `since` - دریافت لاگ‌های بعد از این زمان (فرمت ISO)
*   `level` - فیلتر بر اساس سطح لاگ (ERROR, WARNING, INFO, DEBUG, SUCCESS)
*   `limit` - حداکثر تعداد لاگ‌ها (پیش‌فرض: 50، حداکثر: 100)

**مثال:**

<div dir="ltr">

    curl "http://localhost:8113/logs?level=ERROR&limit=10"
    
</div>

### POST `/logs`

افزودن لاگ جدید

**Body:**

<div dir="ltr">

    {
      "level": "ERROR",
      "message": "یک خطا رخ داد",
      "tags": ["database", "critical"],
      "extra": {
        "user_id": 123,
        "error_code": "DB_001"
      }
    }

</div>
    

### GET `/stats`

دریافت آمار لاگینگ

### POST `/cleanup`

حذف لاگ‌های قدیمی

**پارامترها:**

*   `days` - حذف لاگ‌های قدیمی‌تر از X روز (پیش‌فرض: 30)
*   `seconds` - حذف لاگ‌های قدیمی‌تر از X ثانیه

### GET `/health`

بررسی وضعیت سلامت API

* * *

</div>

<div id="examples">

💡 مثال‌های کاربردی
-------------------

### لاگینگ ساده

<div dir="ltr">

    from logger_api import project_logger
    
    # لاگ ساده
    project_logger.info("برنامه شروع شد")
    
    # لاگ با تگ
    project_logger.error("اتصال ناموفق بود", tags=["network", "critical"])
    
    # لاگ با داده‌های اضافی
    project_logger.warning(
        "استفاده بالای حافظه شناسایی شد",
        tags=["system", "memory"],
        memory_percent=85.2,
        threshold=80
    )

</div>
    

### مدیریت خطاها

<div dir="ltr">

    try:
        # کد شما
        result = risky_operation()
    except Exception as e:
        project_logger.error(
            f"عملیات ناموفق بود: {str(e)}",
            tags=["error", "operation"],
            error_type=type(e).__name__,
            traceback=str(e)
        )

</div>
    

### مانیتورینگ سیستم

<div dir="ltr">

    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=1)
    
    if cpu_percent > 80:
        project_logger.warning(
            f"استفاده بالای CPU: {cpu_percent}%",
            tags=["system", "cpu"],
            cpu_percent=cpu_percent,
            threshold=80
        )

</div>
    

### عملیات Async

<div dir="ltr">

    async def async_task():
        try:
            project_logger.info("شروع تسک async", tags=["async"])
            
            # کد async شما
            await some_async_operation()
            
            project_logger.success("تسک async تکمیل شد", tags=["async"])
        except Exception as e:
            project_logger.error(
                f"تسک async ناموفق بود: {str(e)}",
                tags=["async", "error"]
            )
    

* * *

</div>

</div>

🤖 دستورات ربات
---------------

<div dir="ltr">

- `/start` - نمایش منوی اصلی
- `/add <name> <api_url> <chat_id> [tags]` - افزودن پروژه جدید
- `/remove <name>` - حذف پروژه
- `/list` - لیست تمام پروژه‌ها
- `/start_monitor` - شروع مانیتورینگ تمام پروژه‌ها
- `/stop_monitor` - توقف مانیتورینگ
- `/status` - نمایش وضعیت ربات

* * *

</div>

📊 سطوح لاگ
-----------

- 🔴 ERROR - خطاها و استثناهای برنامه
- 🟡 WARNING - پیام‌های هشدار و مشکلات احتمالی
- 🔵 INFO - پیام‌های اطلاعاتی عمومی
- 🟣 DEBUG - اطلاعات دیباگ برای توسعه
- 🟢 SUCCESS - عملیات‌های موفق

* * *

🔒 نکات امنیتی
--------------

*   فقط کاربر ادمین (تنظیم شده در `config.py`) می‌تواند ربات را کنترل کند
*   فایل `config.py` را خصوصی نگه دارید و هرگز آن را در version control آپلود نکنید
*   در محیط production از environment variables برای داده‌های حساس استفاده کنید
*   برای API در محیط production استفاده از HTTPS را در نظر بگیرید
*   به صورت دوره‌ای لاگ‌های قدیمی را پاک کنید تا فضای دیسک پر نشود

* * *

🐛 عیب‌یابی
-----------

### ربات پاسخ نمی‌دهد

*   بررسی کنید که `ADMIN_USER_ID` صحیح است
*   اعتبار توکن ربات را تأیید کنید
*   مطمئن شوید ربات بدون خطا در حال اجرا است

### لاگ‌ها نمایش داده نمی‌شوند

*   بررسی کنید که آدرس API قابل دسترسی است
*   چک کنید که مانیتورینگ شروع شده است (`/start_monitor`)
*   تأیید کنید که chat\_id صحیح است (برای گروه‌ها/کانال‌ها از اعداد منفی استفاده کنید)

### مشکلات پایگاه داده

*   مجوزهای نوشتن برای دایرکتوری را بررسی کنید
*   تأیید کنید که SQLite به درستی نصب شده است
*   فایل‌های `.db` را حذف کرده و دوباره راه‌اندازی کنید

### خطای Timeout

*   زمان چک کردن پروژه‌ها را افزایش دهید (در `LogGram.py`)
*   تعداد پروژه‌های فعال را کاهش دهید
*   سرعت اینترنت خود را بررسی کنید

* * *

⚡ بهینه‌سازی عملکرد
-------------------

### برای پروژه‌های با ترافیک بالا:

1.  **افزایش زمان چک کردن:** در `LogGram.py` خط زیر را پیدا کنید:

<div dir="ltr">
    
    await asyncio.sleep(3600)  # 1 hour
    await asyncio.sleep(7200)  # 2 hours
        
</div>
    
2.  **استفاده از فیلترهای تگ:** فقط تگ‌های مهم را ارسال کنید (مثلاً `error,critical`)
3.  **پاکسازی خودکار:** یک Cron Job برای پاکسازی روزانه لاگ‌های قدیمی تنظیم کنید

**✅ توصیه:** برای پروژه‌های production، لاگ‌های قدیمی‌تر از 7 روز را به صورت روزانه پاک کنید.

* * *

🎯 سناریوهای استفاده
--------------------

### 1\. مانیتورینگ اپلیکیشن وب

<div dir="ltr">

    from logger_api import project_logger
    
    @app.route('/api/user/register', methods=['POST'])
    def register_user():
        try:
            # کد ثبت نام
            project_logger.success(
                "کاربر جدید ثبت نام کرد",
                tags=["user", "register"],
                user_id=new_user.id,
                email=new_user.email
            )
            return {"status": "success"}
        except Exception as e:
            project_logger.error(
                f"خطا در ثبت نام: {str(e)}",
                tags=["user", "register", "error"],
                error_type=type(e).__name__
            )
            return {"status": "error"}, 500

</div>
    

### 2\. مانیتورینگ دیتابیس

<div dir="ltr">

    import psycopg2
    
    def check_database_health():
        try:
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # چک کردن تعداد کانکشن‌ها
            cursor.execute("SELECT count(*) FROM pg_stat_activity")
            connections = cursor.fetchone()[0]
            
            if connections > 80:
                project_logger.warning(
                    f"تعداد کانکشن‌های دیتابیس زیاد است: {connections}",
                    tags=["database", "connections"],
                    connection_count=connections,
                    threshold=80
                )
            else:
                project_logger.debug(
                    "وضعیت دیتابیس سالم است",
                    tags=["database", "health"],
                    connection_count=connections
                )
                
            conn.close()
        except Exception as e:
            project_logger.error(
                f"خطا در اتصال به دیتابیس: {str(e)}",
                tags=["database", "critical"],
                error_type=type(e).__name__
            )

</div>
    

### 3\. مانیتورینگ Background Jobs

<div dir="ltr">

    from celery import Celery
    
    @celery.task
    def process_payments():
        job_id = str(uuid.uuid4())
        
        project_logger.info(
            f"شروع پردازش پرداخت‌ها - Job: {job_id}",
            tags=["payment", "job", "start"],
            job_id=job_id
        )
        
        try:
            # پردازش پرداخت‌ها
            processed = process_all_payments()
            
            project_logger.success(
                f"پرداخت‌ها پردازش شدند - Job: {job_id}",
                tags=["payment", "job", "completed"],
                job_id=job_id,
                processed_count=processed
            )
        except Exception as e:
            project_logger.error(
                f"خطا در پردازش پرداخت‌ها: {str(e)}",
                tags=["payment", "job", "error"],
                job_id=job_id,
                error_type=type(e).__name__
            )

</div>
    

* * *

🔧 تنظیمات پیشرفته
------------------

### تغییر پورت API

در فایل `logger_api.py`، خط آخر را تغییر دهید:

<div dir="ltr">

    uvicorn.run(
        app,
        host="0.0.0.0",  # برای دسترسی از خارج
        port=8000,       # پورت دلخواه
        log_level="info"
    )

</div>
    

### تغییر زمان چک کردن پروژه‌ها

در فایل `LogGram.py`، در تابع `monitoring_loop`:

<div dir="ltr">

    # هر 30 دقیقه چک کن
    await asyncio.sleep(1800)  # 30 minutes

</div>
    

### افزودن فیلترهای سفارشی

<div dir="ltr">

    from logger_api import project_logger
    
    # فقط لاگ‌های ERROR و CRITICAL
    def log_if_critical(level, message, **kwargs):
        if level in ['ERROR', 'CRITICAL']:
            project_logger.log(level, message, **kwargs)

</div>
    

* * *

📞 پشتیبانی و کمک
-----------------

**سوال دارید؟**

*   برای گزارش مشکلات، یک Issue در repository باز کنید
*   برای پرسیدن سوالات، از بخش Discussions استفاده کنید
*   برای مشارکت در پروژه، Pull Request ارسال کنید

* * *

📜 مجوز استفاده
---------------

این پروژه متن‌باز بوده و برای استفاده شخصی و تجاری در دسترس است.

* * *

🤝 مشارکت
---------

مشارکت‌ها، گزارش مشکلات و درخواست‌های ویژگی جدید همیشه خوش‌آمدند!

**چگونه مشارکت کنیم؟**

1.  پروژه را Fork کنید
2.  یک Branch جدید بسازید (`git checkout -b feature/AmazingFeature`)
3.  تغییرات خود را Commit کنید (`git commit -m 'Add some AmazingFeature'`)
4.  به Branch خود Push کنید (`git push origin feature/AmazingFeature`)
5.  یک Pull Request باز کنید

* * *

🙏 تشکر ویژه
------------

از تمام کسانی که در توسعه این پروژه مشارکت کرده‌اند، تشکر می‌کنیم.

* * *

❤️ ساخته شده با عشق برای لاگینگ بهتر
------------------------------------

اگر این پروژه برای شما مفید بود، یک ⭐ در GitHub به ما بدهید!

</div>