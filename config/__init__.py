from . import env_config, json_config

# Credentials
BOT_TOKEN = env_config.BOT_TOKEN or json_config.BOT_TOKEN

# Throw error if credentials are missing
if not BOT_TOKEN:
    raise EnvironmentError("BOT_TOKEN not set!")
