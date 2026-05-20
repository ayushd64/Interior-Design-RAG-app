# auth/firebase_auth.py
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from typing import Optional, Dict
from dotenv import load_dotenv
import os

load_dotenv()

# ─────────────────────────────────────────────────
# Firebase Auth Initialization
# ─────────────────────────────────────────────────
def initialize_firebase_auth():
    """
    Initialize Firebase Admin SDK for authentication
    Uses same credentials as Firestore!
    """
    if not firebase_admin._apps:
        credentials_path = os.getenv(
            "FIREBASE_CREDENTIALS_PATH",
            "./firebase-credentials.json"
        )
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Auth initialized!")

# ─────────────────────────────────────────────────
# Verify Firebase ID Token
# ─────────────────────────────────────────────────
async def verify_token(
    id_token: str
) -> Optional[Dict]:
    """
    Verify Firebase ID token sent from frontend
    
    Returns:
        Dict with user info if valid
        None if invalid
    """
    try:
        # Make sure Firebase Auth is initialized
        initialize_firebase_auth()
        
        # Verify the token
        decoded_token = firebase_auth.verify_id_token(
            id_token,
            check_revoked=True
        )
        
        # Return user info
        return {
            "uid"           : decoded_token["uid"],
            "email"         : decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False),
            "name"          : decoded_token.get("name"),
            "picture"       : decoded_token.get("picture")
        }
        
    except firebase_auth.RevokedIdTokenError:
        print("❌ Token has been revoked")
        return None
    except firebase_auth.ExpiredIdTokenError:
        print("❌ Token has expired")
        return None
    except firebase_auth.InvalidIdTokenError as e:
        print(f"❌ Invalid token: {e}")
        return None
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return None

