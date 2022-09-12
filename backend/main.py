from fastapi import FastAPI, Depends
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred)

app = FastAPI()
