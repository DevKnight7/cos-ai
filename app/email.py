from fastapi import APIRouter, HTTPException, Request
import requests

router = APIRouter()

@router.get("/emails/search")
async def search_emails(request: Request, since: str):
    try:
        emails_found = fetch_emails(request, since)
        return emails_found["resultSizeEstimate"] > 0

    except HTTPException as exc:
        raise exc

def fetch_emails(request: Request, since: str):
    query = f"after:{since}"
    token = request.session.get("token")

    if not token or "access_token" not in token:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    headers = {
        'Authorization': f"Bearer {token['access_token']}",
    }

    url = f"https://www.googleapis.com/gmail/v1/users/me/messages?q={query}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch emails.")

        return response.json()

    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=f"Failed to make a request to {url}: {exc}")
