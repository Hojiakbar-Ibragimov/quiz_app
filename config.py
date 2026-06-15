from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))