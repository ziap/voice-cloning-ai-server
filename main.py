#!/usr/bin/env python

from fastapi import FastAPI
from routes import router

import uvicorn

from dotenv import load_dotenv
from os import environ as env

load_dotenv()

HOST = env.get('HOST', '127.0.0.1')
PORT = int(env.get('PORT', 3000))
DEBUG = bool(env.get('DEBUG', False))

app = FastAPI()
app.include_router(router)


if __name__ == '__main__':
    if DEBUG:
        uvicorn.run('main:app', host=HOST, port=PORT, reload=True)
    else:
        uvicorn.run(app, host=HOST, port=PORT)

