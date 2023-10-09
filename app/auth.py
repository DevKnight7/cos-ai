from fastapi import APIRouter, HTTPException, Request, Depends
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from decouple import config
from fastapi_msal import MSALAuthorization, UserInfo, MSALClientConfig
import secrets

config_data = {
    'GOOGLE_CLIENT_ID': config("GOOGLE_CLIENT_ID"),
    'GOOGLE_CLIENT_SECRET': config("GOOGLE_CLIENT_SECRET"),
    'MICROSOFT_CLIENT_ID': config("MICROSOFT_CLIENT_ID"),
    'MICROSOFT_CLIENT_SECRET': config("MICROSOFT_CLIENT_SECRET"),
}
redirect_uri = {
    "google":config("GOOGLE_REDIRECT_URI"),
    "microsoft":config("MICROSOFT_REDIRECT_URI"),
}

starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)

# Register OAuth providers (Google and Microsoft)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/gmail.readonly'},
)

oauth.register(
    name='microsoft',
    server_metadata_url='https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile https://graph.microsoft.com/mail.read'},
)
def get_oauth_provider(email):
    if email.endswith("gmail.com"):
        return oauth.google, redirect_uri["google"]
    elif email.endswith("microsoft.com"):
        return oauth.microsoft, redirect_uri["microsoft"]
    else:
        raise HTTPException(status_code=400, detail="Unsupported email domain")

router = APIRouter()

@router.get(redirect_uri["microsoft"])
async def fu2(request: Request):
    try:
        # access_token = await oauth.google.authorize_access_token(request
        stored_state = request.session.get("oauth_state")

        print("Request ----------> ", stored_state)

        access_token = await oauth.microsoft.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.get("/connect/email")
async def authenticate_with_email(request: Request):
    email = request.query_params.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required.")

    # Determine the OAuth provider based on the email domain
    oauth_provider, redirect_url = get_oauth_provider(email)

    try:
        response = await oauth_provider.authorize_redirect(request, redirect_url)
        print("------------------------------", response.status_code)
        return response
    except OAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))

@router.get(redirect_uri["google"])
async def oauth_callback(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
        request.session["token"] = access_token
        user_data = await oauth.google.parse_id_token(request, access_token)
    except OAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    return {"user_data": user_data}
