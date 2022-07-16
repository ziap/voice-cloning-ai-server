from dotenv import load_dotenv
from os import environ as env

load_dotenv()

HOST = env.get('HOST', '127.0.0.1')
PORT = int(env.get('PORT', 3000))
DEBUG = bool(env.get('DEBUG', False))
