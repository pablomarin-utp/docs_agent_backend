from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.config.load import (
    GOOGLE_CLOUD_CLIENT_ID,
    GOOGLE_CLOUD_CLIENT_SECRET,
)

config_data = {
    'GOOGLE_CLIENT_SECRET': GOOGLE_CLOUD_CLIENT_SECRET,
    'GOOGLE_CLIENT_ID': GOOGLE_CLOUD_CLIENT_ID,
}

config = Config(environ=config_data)

oauth = OAuth(config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)