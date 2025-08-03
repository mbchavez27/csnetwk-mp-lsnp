import time
import secrets
from tokens.validator import validate_token

def build_like_message (sender_id: str, receiver_id: str, post_timestamp: int, action, token: str) -> str:
    return f"""TYPE: LIKE
FROM: {sender_id}
TO: {receiver_id}
POST_TIMESTAMP: {post_timestamp}
ACTION: {action.upper()}
TIMESTAMP: {int(time.time())}
TOKEN: {token}

"""

def handle_like(message:dict, peer_table, user_profile, logger =None):
    sender_id = message.get("FROM")
    receiver_id = message.get("TO")
    post_timestamp = message.get("POST_TIMESTAMP")
    action = message.get("ACTION")
    token = message.get("TOKEN")

    if not validate_token(token, expected_scope="broadcast"):
        if logger:
            logger.warning(f"[LIKE] Invalid token from {sender_id}")
        return

    if receiver_id != peer_table.own_id:
        return

    logger.debug(f"[DEBUG] recent_posts keys: {list(user_profile['recent_posts'].keys())}")
    key = (message["TO"], int(message["POST_TIMESTAMP"]))
    logger.debug(f"[DEBUG] Looking up key: {key}")
    content = user_profile["recent_posts"].get(key, "[unknown message]")


    display_name = peer_table.get_name(sender_id)

    if action == "LIKE":
        print(f"{display_name} likes your post [post{content}]")
    elif action == "UNLIKE":
        print(f"{display_name} unliked your post [post{content}]")
    else:
        print(f"Unknown action in LIKE message: {action}")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received {action} for post {post_timestamp} from {sender_id}\n{message}")


