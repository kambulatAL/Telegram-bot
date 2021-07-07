from environs import Env


env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
IP = env.str("ip")

BLOCKCYPHER_TOKEN = env.str("BLOCKCYPHER_TOKEN")
BTC_WALLET = env.str("BTC_WALLET")

PG_USER = env.str("DB_USER")
PG_PASSWORD = env.str("DB_PASSWORD")
DATABASE = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")

POSTGRES_URI = f"postgresql://{PG_USER}:{PG_PASSWORD}@{DB_HOST}/{DATABASE}"