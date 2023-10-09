from fastapi import FastAPI
from app import email, openai, auth
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="AE87463CA22A17A7F43A68F968D3F")

# OAuth authentication endpoint
app.include_router(auth.router)

# Endpoint to check if user has received emails since a timestamp
app.include_router(email.router)

# Endpoint to calculate the cost of processing emails with GPT-4
app.include_router(openai.router)
