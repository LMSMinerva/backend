import os
import requests
import urllib.parse
import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from dotenv import load_dotenv

load_dotenv()

def get_id_token_with_code(code):
    """
    Verify Google authentication code and return user information.
    
    Args:
        code (str): Authorization code from Google OAuth
    
    Returns:
        dict: Verified token information or None if verification fails
    """
    redirect_uri = "https://minerva-lms.vercel.app/authorize"
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

    try:
        response = requests.post(token_endpoint, data=body, headers=headers)
        print("Token endpoint response:", response.json())  # Debug log

        if response.ok:
            id_token_str = response.json().get('id_token')
            id_info = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                os.getenv('CLIENT_ID')
            )
            print("Verified token info:", id_info)  # Debug log
            if not id_info.get('email'):
                # If email not in token, fetch from userinfo endpoint
                access_token = response.json().get('access_token')
                userinfo = requests.get(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    headers={'Authorization': f'Bearer {access_token}'}
                ).json()
                id_info['email'] = userinfo.get('email')
            
                return id_info
            return {
                'email': id_info.get('email'),
                'given_name': id_info.get('given_name', ''),
                'family_name': id_info.get('family_name', ''),
                'picture': id_info.get('picture', ''),
                'gender': id_info.get('gender', ''),
                'birthday': id_info.get('birthdate', None),
                'sub': id_info.get('sub'),  # Add Google user ID
                'locale': id_info.get('locale', '')
            }
        print("Token endpoint error:", response.json())
        return None
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return None
