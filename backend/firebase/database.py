# Database
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("./serviceAccountKey.json")

# Currently Firebase Realtime Database is linked to the bzacapstonechc firebase acc's proj
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://chcdashboard-default-rtdb.asia-southeast1.firebasedatabase.app"
})
