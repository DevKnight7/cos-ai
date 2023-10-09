from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app
from app.email import router
from unittest.mock import patch

# Create a test client with the FastAPI 'app'
client = TestClient(app)

# Define test cases

@patch('app.email.fetch_emails')
def test_search_emails_successful(mock_fetch_emails):
    # Mock fetch_emails function
    mock_fetch_emails.return_value = {"resultSizeEstimate": 5}

    # Send a request to /emails/search
    response = client.get("/emails/search?since=2023-01-01")

    assert response.status_code == 200
    assert response.json() is True

def test_search_emails_unauthenticated():
    # Test case for unauthenticated request.

    # Mock fetch_emails function
    def mock_fetch_emails(request, since):
        raise HTTPException(status_code=401, detail="Not authenticated.")

    # Replace the fetch_emails function with our mock
    router.fetch_emails = mock_fetch_emails

    # Send a request to /emails/search
    response = client.get("/emails/search?since=2023-01-01", cookies={"session": "mock_session_key"})

    assert response.status_code == 401
    assert "detail" in response.json()

@patch('app.email.fetch_emails')
def test_search_emails_failed(mock_fetch_emails):
    # Mock fetch_emails function
    mock_fetch_emails.side_effect = HTTPException(status_code=500, detail="Failed to fetch emails.")

    # Send a request to /emails/search
    response = client.get("/emails/search?since=2023-01-01", cookies={"session": "mock_session_key"})

    assert response.status_code == 500
    assert "detail" in response.json()
