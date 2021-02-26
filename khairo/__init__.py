from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from mongoengine import connect, disconnect

from khairo.backend.view import accountView, serviceView
from khairo.settings import DEBUG, DATABASE_URI

app = FastAPI(debug=DEBUG)
app.mount("/static", StaticFiles(directory="./khairo/backend/static"), name="static")


@app.get("/", include_in_schema=False)
async def docs():
    return RedirectResponse("/docs", status_code=302)


app.include_router(accountView.router)
app.include_router(serviceView.service_router)
app.include_router(serviceView.option_router)
app.include_router(serviceView.category_router)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
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
