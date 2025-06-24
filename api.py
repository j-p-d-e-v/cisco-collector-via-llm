from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Union
import json
from agent import send_prompt

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def prompt(prompt: str = ""):
    retry = 3
    while retry !=0:
        try:
            output = send_prompt(prompt)
            if output is None or output == "":
                retry -= 1
                continue
            return output
        except:
            retry -= 1