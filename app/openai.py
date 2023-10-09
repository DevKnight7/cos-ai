from fastapi import APIRouter, Request, HTTPException
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import tiktoken
import requests
import base64
from app.email import fetch_emails

router = APIRouter()

@router.get("/cost")
async def calculate_cost(request: Request):
    emails = fetch_emails_content(request)

    number_of_tokens = num_tokens_from_string(emails)

    cost = (number_of_tokens / 1000) * 0.03  # Gpt-4 cost 0.03 dollars per 1000 tokens

    return {"cost_in_dollars": cost}

def num_tokens_from_string(text: str):
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    num_tokens = len(encoding.encode(text))
    return num_tokens

def base64_decode(encoded_data):
    return base64.urlsafe_b64decode(encoded_data.encode('utf-8')).decode('utf-8')

def fetch_emails_content(request: Request):
    since = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    response = fetch_emails(request, since)

    messages = response.get('messages', [])

    token = request.session.get("token")

    headers = {
        'Authorization': f"Bearer {token['access_token']}",
    }

    content = ""

    for message in messages:
        message_id = message['id']
        message_response = requests.get(
            f"https://www.googleapis.com/gmail/v1/users/me/messages/{message_id}",
            headers=headers
        )

        if message_response.status_code == 200:
            email_content = message_response.json()
            text_html = ""

            if email_content['payload']['body']['size'] > 0:
                text_html = base64_decode(email_content['payload']['body']['data'])

            soup = BeautifulSoup(text_html, 'html.parser')

            email_body = soup.get_text()
            content += f"{email_body} \n"
        else:
            print(f"Failed to fetch message {message_id}")

    return content
