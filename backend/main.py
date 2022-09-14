import samplecode
from fastapi import FastAPI, Depends
import api.samplefacebookapi

app = FastAPI()
samplecode.sample(app)
api.samplefacebookapi.sample(app)