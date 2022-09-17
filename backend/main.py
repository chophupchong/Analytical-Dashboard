from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from firebase import database
from routers import youtube  # , facebook, instagram
# Database
# import firebase_admin
# from firebase_admin import credentials

# cred = credentials.Certificate("./serviceAccountKey.json")

# # Currently Firebase Realtime Database is linked to the bzacapstonechc firebase acc's proj
# firebase_admin.initialize_app(cred, {
#     'databaseURL': "https://chcdashboard-default-rtdb.asia-southeast1.firebasedatabase.app"
# })

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(youtube.router)
# app.include_router(facebook.router)
# app.include_router(instagram.router)
