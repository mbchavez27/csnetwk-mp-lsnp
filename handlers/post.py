import time
import secrets
from tokens.validator import validate_token

def build_post_message(user_id: str, content: str, token: str, ttl: int = 3600) -> str:
    return f"""TYPE: POST
USER_ID: {user_id}
CONTENT: {content}
TTL: {ttl}
MESSAGE_ID: {secrets.token_hex(8)}
TOKEN: {token}

"""

def handle_post(message: dict, peer_table, logger=None):
    user_id = message.get("USER_ID")
    content = message.get("CONTENT", "")
    token = message.get("TOKEN")
    ttl = int(message.get("TTL", 3600))

    if not validate_token(token, expected_scope="broadcast"):
        print(f"[WARNING] Invalid token from {user_id}")
        return
    
    if not peer_table.is_following(user_id):
        return  # Ignore post from non-followed users
    
    display_name = peer_table.get_name(user_id)
    print(f"[POST] {display_name}: {content}")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received POST:\n{message}")
