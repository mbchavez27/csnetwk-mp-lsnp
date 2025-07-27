import time

def generate_token(user_id: str, ttl: int, scope: str) -> str:
    """
    Create a token in the format: user_id|expires_at|scope
    """
    expires_at = int(time.time()) + ttl
    return f"{user_id}|{expires_at}|{scope}"