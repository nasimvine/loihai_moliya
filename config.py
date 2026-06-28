"""
Файли танзимоти умумии система
Дар ин ҷо маълумоти махфӣ ва танзимоти асосӣ нигоҳ дошта мешаванд
"""
import os

# --- Танзимоти Telegram Bot ---
BOT_TOKEN = "8958152466:AAEIJBHqMtHSQSqz1rEwbTCRnPnpzi6jXls"
BOT_USERNAME = "@hisoboti_nasim_bot"
ALLOWED_USER_ID = 8095678119  # Фақат ин корбар метавонад истифода кунад

# --- Танзимоти сервер ва база ---
API_HOST = "127.0.0.1"
API_PORT = 8000
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "baza.db")
CURRENCY = "сомон"

# --- Танзимоти дигар ---
TIME_ZONE = "Asia/Dushanbe"
DATE_FORMAT = "%d.%m.%Y"
DATETIME_FORMAT = "%d.%m.%Y %H:%M"