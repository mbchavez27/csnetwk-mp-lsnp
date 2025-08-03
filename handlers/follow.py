# To Test FOLLOW / UNFOLLOW:
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
# 3. Expected Output:
#    - Terminal 1 (Bella):
#        You followed Edward@127.0.0.3
#
#    - Terminal 2 (Edward):
#        [FOLLOW] User Bella has followed you
#
# 4. To Unfollow:
#     /unfollow Edward@127.0.0.3
#
# 5. Expected Output:
#    - Terminal 1:
#        You unfollowed Edward@127.0.0.3
#
#    - Terminal 2:
#        [FOLLOW] User Bella has unfollowed you

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

