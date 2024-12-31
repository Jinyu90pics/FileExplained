import os
from dotenv import load_dotenv

load_dotenv(".env")

OPENAI_KEY = os.getenv('OPENAI_KEY')
