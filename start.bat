@echo off
REM Start companion app in a new window
start "" python companion_app.py
REM Start Discord bot in the current window
python bot.py
