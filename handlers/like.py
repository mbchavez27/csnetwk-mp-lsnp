# TODO: Implement LIKE message handling in like.py
# see RFC for detailed info
# 
# NOTE: use (if logger and logger.verbose:) for conditional verbose logging
#     : tokens can be hardcoded for now
# add your commands in commands.py and call handlers in dispatcher.py

import time
import secrets

def build_like_message (sender_id: str, receiver_id: str, post_timestamp: int, action="LIKE", ttl=3600):
    timestamp = int(time.time())
    expires = timestamp + ttl
    token = f"{sender_id}|{expires}|broadcast"
    message_id = secrets.token_hex(8)

    return f"""TYPE: LIKE
MESSAGE_ID: {message_id}
FROM: {sender_id}
TO: {receiver_id}
POST_TIMESTAMP: {post_timestamp}
ACTION: {action}
TIMESTAMP: {timestamp}
TOKEN: {token}

"""

def handle_like(message:dict, peer_table, logger =None):
    sender_id = message.get("FROM")
    post_timestamp = message.get("POST_TIMESTAMP")
    action = message.get("ACTION", "LIKE")

    display_name = peer_table.get(sender_id, sender_id)

    if action == "LIKE":
        print(f"{display_name} likes your post [post{post_timestamp}]")
    elif action == "UNLIKE":
        print(f"{display_name} unliked your post [post{post_timestamp}]")
    else:
        print(f"Unknown action in LIKE message: {action}")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received {action} for post {post_timestamp} from {sender_id}\n{message}")


