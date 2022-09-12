from typing import Union
from fastapi import FastAPI
import firebase_admin
from firebase_admin import firestore_async

# Application Default credentials are automatically created.
app = firebase_admin.initialize_app()
db = firestore_async.client()

app = FastAPI()
