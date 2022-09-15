import samplecode
import api.instagramapi
from fastapi import FastAPI, Depends
import api.samplefacebookapi

app = FastAPI()
samplecode.sample(app)
api.samplefacebookapi.sample(app)
api.instagramapi.sample(app)
