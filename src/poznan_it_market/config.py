import os
from dotenv import load_dotenv

load_dotenv()
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
JJIT_API_URL = os.environ["JJIT_API_URL"]
DATABASE_URL = os.environ["DATABASE_URL"]
