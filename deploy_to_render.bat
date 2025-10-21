@echo off
echo 🚀 تحضير البوت للنشر على Render
echo ================================

REM Configure git
git config user.name "DiscordBot"
git config user.email "bot@example.com"

REM Add all files
git add .

REM Commit changes
git commit -m "Discord Video Bot v2.1.0 - Ready for Render"

echo ✅ تم تحضير البوت للنشر!
echo.
echo 📋 الخطوات التالية:
echo 1. أنشئ مستودع جديد على GitHub
echo 2. انسخ رابط المستودع
echo 3. شغل الأمر التالي:
echo    git remote add origin [رابط_المستودع]
echo    git push -u origin main
echo 4. اذهب إلى render.com وأنشئ Web Service
echo 5. اربط المستودع وأضف التوكن
echo.
pause
