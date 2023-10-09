from fastapi.testclient import TestClient
from main import app
from app.auth import oauth
from authlib.integrations.starlette_client import OAuthError
from starlette.responses import RedirectResponse  # Import RedirectResponse

client = TestClient(app)

def test_authenticate_with_microsoft():
    response = client.get("/connect/email?email=example@gmail.com")
    assert response.status_code == 302

def test_authenticate_with_google():
    # Test case with a Google email domain
    email = "user@gmail.com"
    response = client.get(f"/connect/email?email={email}")
    assert "google" in response.url

def test_authenticate_failed():
    response = client.get("/connect/email")
    assert response.status_code == 400

def test_oauth_callback():

    class MockOAuthResponse:
        def authorize_redirect(self, request, redirect_uri):
            # Use RedirectResponse to return a 302 response
            return RedirectResponse(redirect_uri)

        async def authorize_access_token(self, request):
            return {"access_token": "mock_access_token"}

        async def parse_id_token(self, request, access_token):
            return {"sub": "mock_user_id", "email": "mock@example.com"}

    oauth.google = MockOAuthResponse()

    response = client.get("/auth")
    assert response.status_code == 200
    assert "user_data" in response.json()

def test_oauth_error_handling():
    # Mock OAuth error
    class MockOAuthError:
        async def authorize_access_token(self, request):
            raise OAuthError("Mock OAuth Error")

    oauth.google = MockOAuthError()

    response = client.get("/auth")
    assert response.status_code == 404
    assert "detail" in response.json()
