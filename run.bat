@echo off
echo 🚀 بدء تشغيل بوت تحميل الفيديوهات
echo =====================================

REM Check if Python is installed
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت! يرجى تثبيت Python 3.8 أو أحدث
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  ملف .env غير موجود!
    echo يرجى إنشاء ملف .env وإضافة DISCORD_BOT_TOKEN
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist venv (
    echo 📦 إنشاء البيئة الافتراضية...
    py -m venv venv
)

echo 📦 تفعيل البيئة الافتراضية...
call venv\Scripts\activate.bat

echo 📦 تثبيت المتطلبات...
pip install -r requirements.txt

echo 🤖 تشغيل البوت...
py bot.py

pause
