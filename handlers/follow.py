import time
import secrets
from tokens.validator import validate_token

def build_follow_message(sender_id: str, receiver_id: str, token: str) -> str:
    return f"""TYPE: FOLLOW
MESSAGE_ID: {secrets.token_hex(8)}
FROM: {sender_id}
TO: {receiver_id}
TIMESTAMP: {int(time.time())}
TOKEN: {token}

"""

def build_unfollow_message(sender_id: str, receiver_id: str, token: str) -> str:
    return f"""TYPE: UNFOLLOW
MESSAGE_ID: {secrets.token_hex(8)}
FROM: {sender_id}
TO: {receiver_id}
TIMESTAMP: {int(time.time())}
TOKEN: {token}

"""

def handle_follow(message: dict, peer_table, logger=None):
    sender_id = message.get("FROM")
    receiver_id = message.get("TO")
    token = message.get("TOKEN")

    if not validate_token(token, expected_scope="follow"):
        if logger:
            logger.warn(f"[FOLLOW] Invalid token from {sender_id}")
        return
    
    if receiver_id == peer_table.own_id:
        peer_table.add_follower(sender_id)
        display_name = peer_table.get_name(sender_id)
        print(f"[FOLLOW] User {display_name} has followed you")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received FOLLOW\n{message}")

def handle_unfollow(message: dict, peer_table, logger=None):
    sender_id = message.get("FROM")
    receiver_id = message.get("TO")
    token = message.get("TOKEN")

    if not validate_token(token, expected_scope="follow"):
        if logger:
            logger.warn(f"[FOLLOW] Invalid token from {sender_id}")
        return

    if receiver_id == peer_table.own_id:
        peer_table.remove_follower(sender_id)
        display_name = peer_table.get_name(sender_id)
        print(f"[UNFOLLOW] User {display_name} has unfollowed you")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received UNFOLLOW\n{message}")

