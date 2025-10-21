@echo off
echo Adding Discord Bot Token to Railway...
npx @railway/cli variables --set DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
echo Token added successfully!
pause
