# set global config variables

from environs import Env


env = Env()
env.read_env()




# token for bot
BOT_TOKEN = env.str("BOT_TOKEN")

# admins
admins = env.list("ADMINS")  # admins
ADMINS = [int(admin) for admin in admins]

# Path: data\config.py
