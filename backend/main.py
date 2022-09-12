from fastapi import FastAPI, Depends
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("./serviceAccountKey.json")

# Currently Firebase Realtime Database is linked to Elton's URL (Change accordingly if needed)
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': "https://chc-dashboard-3bfea-default-rtdb.asia-southeast1.firebasedatabase.app"
})

app = FastAPI()
