# test_openai.py
import pytest
from fastapi.testclient import TestClient
from main import app
from app.openai import fetch_emails_content  # Import the function directly

client = TestClient(app)

# Define test cases

@pytest.fixture
def mock_fetch_emails_content(monkeypatch):
    def mock_fetch_emails_content(request):
        return "This is a test email."

    monkeypatch.setattr("app.openai.fetch_emails_content", mock_fetch_emails_content)

def test_calculate_cost(mock_fetch_emails_content):
    response = client.get("/cost")

    assert response.status_code == 200
    assert "cost_in_dollars" in response.json()
    assert response.json()["cost_in_dollars"] == pytest.approx(0.00018, abs=1e-5)

def test_calculate_cost_no_emails(mock_fetch_emails_content):

    def mock_fetch_emails_content(request):
        return ""

    response = client.get("/cost")

    assert response.status_code == 200
    assert "cost_in_dollars" in response.json()

    expected_cost = 0.0
    actual_cost = response.json()["cost_in_dollars"]

    assert pytest.approx(actual_cost, abs=1e-3) == expected_cost


def test_calculate_cost_large_email(mock_fetch_emails_content):
    def mock_fetch_emails_content(request):
        return "This is a very long email " * 10000

    response = client.get("/cost")

    assert response.status_code == 200
    assert "cost_in_dollars" in response.json()
    assert response.json()["cost_in_dollars"] == pytest.approx(0.00018, abs=1e-5)
