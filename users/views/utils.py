import os
import requests
import urllib.parse
import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_id_token_with_code(code):
    """
    Verify Google authentication code and return user information.
    
    Args:
        code (str): Authorization code from Google OAuth
    
    Returns:
        dict: Verified token information or None if verification fails
    """
    redirect_uri = "postmessage"
    token_endpoint = "https://oauth2.googleapis.com/token"
    
    payload = {
        'code': code,
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'), 
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
    }

    body = urllib.parse.urlencode(payload)
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    response = requests.post(token_endpoint, data=body, headers=headers)
    
    if response.ok:
        id_token_str = response.json().get('id_token')
        return id_token.verify_oauth2_token(id_token_str, google_requests.Request(), os.getenv('CLIENT_ID'))
    else:
        print(response.json())
        return None
