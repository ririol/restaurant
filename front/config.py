import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_HTTP = os.environ.get("BACKEND_HTTP")
BACKEND_WS = os.environ.get("BACKEND_WS")
