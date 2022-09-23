from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from firebase import database
from routers import facebook#youtube  # , facebook, instagram

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#app.include_router(youtube.router)
app.include_router(facebook.router)
# app.include_router(instagram.router)
