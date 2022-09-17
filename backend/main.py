from fastapi import FastAPI, Depends
from routers import youtube  # , facebook, instagram

app = FastAPI()
app.include_router(youtube.router)
# app.include_router(facebook.router)
# app.include_router(instagram.router)
