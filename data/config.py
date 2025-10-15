from environs import Env
import os

env = Env()
env.read_env()
BOT_TOKEN: str = env.str("BOT_TOKEN")
ADMINS: list[str] = env.list("ADMINS")
IP: str = env.str("IP")
ADMIN_GROUP_ID: int = env.int("ADMIN_GROUP_ID", -1002765600267)
