from environs import Env

env = Env()
env.read_env()

TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN")
ADMINS = env.list("ADMINS")

FIREBASE_CONFIG = {
    "type": env.str("FIREBASE_TYPE"),
    "project_id": env.str("FIREBASE_PROJECT_ID"),
    "private_key": env.str("FIREBASE_PRIVATE_KEY"),
    "client_email": env.str("FIREBASE_CLIENT_EMAIL"),
    "client_id": env.str("FIREBASE_CLIENT_ID"),
    "auth_uri": env.str("FIREBASE_AUTH_URI"),
    "token_uri": env.str("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": env.str("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": env.str("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": env.str("FIREBASE_UNIVERSE_DOMAIN"),
}
