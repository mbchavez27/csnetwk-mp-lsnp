# To Test POST (Broadcast Message to Followers):
#
# 1. Open two terminals.
#
#    Terminal 1:
#     python main.py --ip 127.0.0.2 --username Bella --status Hello --verbose
#
#    Terminal 2:
#     python main.py --ip 127.0.0.3 --username Edward --status Online --verbose
#
# 2. From Bella’s prompt:
#     /follow Edward@127.0.0.3
#
# 3. From Edward’s prompt:
#     /post Hello followers!
#
# 4. Expected Output:
#    - Terminal 1 (Bella):
#        [POST] Edward: Hello followers!
#

import time
import secrets
from tokens.validator import validate_token

def build_post_message(user_id: str, content: str, token: str, ttl: int = 3600) -> str:
    return f"""TYPE: POST
USER_ID: {user_id}
CONTENT: {content}
TTL: {ttl}
MESSAGE_ID: {secrets.token_hex(8)}
TIMESTAMP: {str(int(time.time()))}
TOKEN: {token}

"""

def handle_post(message: dict, peer_table, user_profile, logger=None):
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

    if "TIMESTAMP" in message and "CONTENT" in message and "USER_ID" in message:
        key = (message["USER_ID"], int(message["TIMESTAMP"]))
        user_profile["recent_posts"][key] = message["CONTENT"]
        if logger:
            logger.debug(f"[DEBUG] Stored post from {message['USER_ID']} at {message['TIMESTAMP']}")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received POST:\n{message}")
