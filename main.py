#!/usr/bin/env python

from fastapi import FastAPI
from routes import router

import uvicorn
import config


app = FastAPI()
app.include_router(router)


if __name__ == '__main__':
    if config.DEBUG:
        uvicorn.run('main:app', host=config.HOST, port=config.PORT, reload=True)
    else:
        uvicorn.run(app, host=config.HOST, port=config.PORT)

