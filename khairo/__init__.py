from fastapi import FastAPI
from mongoengine import connect, disconnect
from fastapi.middleware.cors import CORSMiddleware
from khairo.settings import DEBUG, DATABASE_URI
from khairo.backend.view import accountView
from fastapi.responses import RedirectResponse


app = FastAPI(debug=DEBUG)

@app.get("/")
async  def docs():
    return RedirectResponse("/docs", status_code=302)

app.include_router(accountView.router)
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "GET", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def connectDatabase():
    if connect(host=DATABASE_URI):
        print("database connected")


@app.on_event("shutdown")
def disconnectDatabase():
    if disconnect():
        print("database disconnected")
