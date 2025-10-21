@echo off
echo Installing Discord Bot Requirements...
echo ====================================

py --version
if errorlevel 1 (
    echo Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo Installing packages...
py -m pip install --upgrade pip
py -m pip install discord.py
py -m pip install yt-dlp
py -m pip install aiohttp
py -m pip install python-dotenv

if not exist .env (
    echo Creating .env file...
    echo DISCORD_BOT_TOKEN=PUT_YOUR_BOT_TOKEN_HERE > .env
    echo.
    echo IMPORTANT: Update .env file with your Discord bot token
    echo Get token from: https://discord.com/developers/applications
)

echo.
echo Setup complete!
echo To run bot: .\run.bat
pause
