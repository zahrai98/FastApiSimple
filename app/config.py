from fastapi import FastAPI
from routers import users, file


app = FastAPI()
app.include_router(users.router, tags=['users'])
app.include_router(file.router, tags=['file'])