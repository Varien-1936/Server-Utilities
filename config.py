from os import getenv
from sqlite3 import connect
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("token")
HA_WEBHOOK = getenv("ha_webhook")
HAZE_WEBHOOK = getenv("haze_webhook")

db = connect('database.db')

hazead = 925790259160166460
loa = 704888699590279221
lss = 841671029066956831
orleans = 740584420645535775
