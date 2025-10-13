from environs import Env
import os
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  
ADMINS = env.list("ADMINS")  
IP = env.str("ip")  
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", "-1002765600267"))