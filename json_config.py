import json

try:
    with open('config.json', 'r') as json_config_file:
        config = json.load(json_config_file)
except FileNotFoundError:
    config = {}

# Prefix configuration
BOT_TOKEN = config.get('BOT_TOKEN')
