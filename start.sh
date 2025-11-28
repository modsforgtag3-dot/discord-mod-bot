#!/bin/bash
# Run companion app in background
python companion_app.py &
# Run Discord bot
python bot.py
