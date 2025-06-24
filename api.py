from fastapi import FastAPI
from typing import Union
import json
from agent import send_prompt

app = FastAPI()

@app.get("/")
def prompt(prompt: str = ""):
    output = send_prompt(prompt)
    return output
        