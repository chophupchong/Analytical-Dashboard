from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from firebase import database

from routers import facebook  # facebook, instagram
from routers import meta
from routers import googleAds
from routers import youtube
app = FastAPI()

origins = [
    "http://localhost:8080"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(facebook.router)
app.include_router(meta.router)
app.include_router(youtube.router)
app.include_router(googleAds.router)
# app.include_router(instagram.router)
