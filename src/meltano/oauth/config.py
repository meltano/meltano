import os
from secrets import token_hex

# session are used internally to verify the tokens
SECRET_KEY = token_hex(64)
FACEBOOK_CLIENT_ID = os.getenv("OAUTH_FACEBOOK_CLIENT_ID")
FACEBOOK_CLIENT_SECRET = os.getenv("OAUTH_FACEBOOK_CLIENT_SECRET")
