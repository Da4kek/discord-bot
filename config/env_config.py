# If you're on bash (or any other posix-complaint shell) then you can use:
# export BOT_TOKEN='your-token-obtained-from-discord'
# to set a variable for the current shell session or use:
# BOT_TOKEN='your-token-obtained-from-discord' python3 bot.py
# to set it for a single command or edit your /etc/environment file (not suggested at all)
# to set the value permanently

import os


BOT_TOKEN = os.environ.get('BOT_TOKEN')
