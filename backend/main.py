import samplecode
from fastapi import FastAPI, Depends

app = FastAPI()
samplecode.sample(app)