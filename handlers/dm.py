import time
import secrets
from tokens.validator import validate_token

def build_dm_message(sender_id: str, receiver_id: str, content: str, token: str) -> str:
    timestamp = int(time.time())
    message_id = secrets.token_hex(8)

    return f"""TYPE: DM
FROM: {sender_id}
TO: {receiver_id}
CONTENT: {content}
TIMESTAMP: {timestamp}
MESSAGE_ID: {message_id}
TOKEN: {token}
    
"""

def handle_dm(message: dict, peer_table, logger =None):
    sender_id = message.get("FROM")
    content = message.get("CONTENT", "")
    token = message.get("TOKEN")

    if not validate_token(token, expected_scope="chat"):
        if logger:
            logger.warn(f"Invalid DM token from {sender_id}")
        return
    
    display_name = peer_table.get_name(sender_id)
    print(f"[DM] {display_name}: {content}")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received DM\n{message}")
