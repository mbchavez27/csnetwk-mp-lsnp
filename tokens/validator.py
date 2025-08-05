import time
import hashlib

revoked_tokens = set()  

def validate_token(token: str, expected_scope: str) -> bool:
    parts = token.strip().split("|")
    if len(parts) != 3:
        return False

    user_id, expires_at_str, scope = parts

    # Check expiration
    try:
        expires_at = int(expires_at_str)
    except ValueError:
        return False

    if time.time() > expires_at:
        return False  # Expired

    # Check scope
    if scope != expected_scope:
        return False

    # Check revocation
    if is_token_revoked(token):
        return False

    return True

def is_token_revoked(token: str) -> bool:
    return _hash_token(token) in revoked_tokens

def revoke_token(token: str):
    revoked_tokens.add(_hash_token(token))

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
