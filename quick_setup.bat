@echo off
chcp 65001 >nul
echo 🚀 إعداد سريع لبوت تحميل الفيديوهات
echo ==========================================

REM Check Python
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت!
    echo يرجى تحميل Python من: https://python.org
    pause
    exit /b 1
)

echo ✅ Python متوفر

REM Install requirements
echo 📦 تثبيت المتطلبات...
py -m pip install --upgrade pip
py -m pip install discord.py==2.3.2 yt-dlp==2023.10.13 aiohttp==3.9.1 python-dotenv==1.0.0

REM Create .env if not exists
if not exist .env (
    echo 📝 إنشاء ملف .env...
    echo DISCORD_BOT_TOKEN=ضع_توكن_البوت_هنا > .env
    echo ⚠️  يرجى تحديث ملف .env بتوكن البوت الخاص بك
    echo.
    echo 📋 للحصول على التوكن:
    echo 1. اذهب إلى: https://discord.com/developers/applications
    echo 2. أنشئ تطبيق جديد
    echo 3. اذهب إلى Bot واحصل على التوكن
    echo 4. ضع التوكن في ملف .env
    echo.
    pause
) else (
    echo ✅ ملف .env موجود
)

echo.
echo ✅ الإعداد مكتمل!
echo 🚀 لتشغيل البوت: .\run.bat
echo.
pause
