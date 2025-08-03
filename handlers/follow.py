# TODO: Implement FOLLOW and UNFOLLOW message handlers
# see RFC for detailed info
#
# =========================
# FOLLOW Message Structure:
# =========================
# TYPE: FOLLOW
# MESSAGE_ID:                   # Unique message ID
# FROM: <string>                # Follower's user_id (e.g., e.g., username@ipaddress)
# TO: <string>                  # Followed user's user_id
# TIMESTAMP: 
# TOKEN: <string>               # Format: user_id|timestamp|follow (hardcoded for now)
#
# ============================
# UNFOLLOW Message Structure:
# ============================
# TYPE: UNFOLLOW
# MESSAGE_ID:                   # Unique message ID
# FROM: <string>                # Unfollower's user_id
# TO: <string>                  # Unfollowed user's user_id
# TIMESTAMP: 
# TOKEN: <string>               # Format: user_id|timestamp|follow (hardcoded for now)
# 
# NOTE: use (if logger and logger.verbose:) for conditional verbose logging
# add your commands in commands.py and call handlers in dispatcher.py

import time
import secrets

def build_follow_message(sender_id: str, receiver_id: str, ttl=3600):
    timestamp = int(time.time())
    expires = timestamp + ttl
    token = f"{sender_id}|{expires}|follow"
    message_id = secrets.token_hex(8)

    return f"""TYPE: FOLLOW
MESSAGE_ID: {message_id}
FROM: {sender_id}
TO: {receiver_id}
TIMESTAMP: {timestamp}
TOKEN: {token}

"""

def build_unfollow_message(sender_id: str, receiver_id: str, ttl=3600):
    timestamp = int(time.time())
    expires = timestamp + ttl
    token = f"{sender_id}|{expires}|follow"
    message_id = secrets.token_hex(8)

    return f"""TYPE: UNFOLLOW
MESSAGE_ID: {message_id}
FROM: {sender_id}
TO: {receiver_id}
TIMESTAMP: {timestamp}
TOKEN: {token}

"""

def handle_follow(message: dict, peer_table, logger=None):
    sender_id = message.get("FROM")

    display_name = peer_table.get(sender_id, sender_id)

    print(f"User {display_name} has followed you")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received FOLLOW\n{message}")

def handle_unfollow(message: dict, peer_table, logger=None):
    sender_id = message.get("FROM")

    display_name = peer_table.get(sender_id, sender_id)

    print(f"User {display_name} has unfollowed you")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received UNFOLLOW\n{message}")

