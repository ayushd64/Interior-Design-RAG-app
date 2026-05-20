# auth/dependencies.py
from fastapi import HTTPException, Header, status
from typing import Optional
from auth.firebase_auth import verify_token

# ─────────────────────────────────────────────────
# Auth Dependency for Protected Routes
# ─────────────────────────────────────────────────
async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Extract and verify Firebase token from header
    
    Header format:
    Authorization: Bearer <firebase-id-token>
    
    Returns:
        dict with user info (uid, email, etc.)
    
    Raises:
        HTTPException if not authenticated
    """
    
    # ── Check Authorization Header ────────────────
    if not authorization:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Authorization header missing",
            headers     = {"WWW-Authenticate": "Bearer"}
        )
    
    # ── Check Bearer Format ───────────────────────
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Invalid authorization format. Use 'Bearer <token>'",
            headers     = {"WWW-Authenticate": "Bearer"}
        )
    
    # ── Extract Token ─────────────────────────────
    token = authorization.split("Bearer ")[1].strip()
    
    if not token:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Token is empty"
        )
    
    # ── Verify Token ──────────────────────────────
    user = await verify_token(token)
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Invalid or expired token",
            headers     = {"WWW-Authenticate": "Bearer"}
        )
    
    # ── Require Email Verification ────────────────
    if not user.get("email_verified", False):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail      = "Email not verified. Please verify your email first."
        )
    
    return user

# ─────────────────────────────────────────────────
# Optional Auth (User info if available)
# ─────────────────────────────────────────────────
async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """
    Get user info if authenticated
    Returns None if not authenticated (no error)
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None

