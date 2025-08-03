# TODO: Implement POST message handler
#
# This function should handle incoming TYPE: POST messages.
# see RFC for detailed info
#
# Expected fields:
# - TYPE: POST
# - USER_ID: <string>        # Format: username@ipaddress
# - CONTENT: <string>        
# - TTL:                      
# - MESSAGE_ID:               # Randomly generated 64-bit binary in hex format
# - TOKEN: <string>           # Format: USER_ID|<timestamp + TTL>|broadcast (hardcoded for now)
#
# NOTE: use (if logger and logger.verbose:) for conditional verbose logging
# add your commands in commands.py and call handlers in dispatcher.py

import time
import secrets

def build_post_message(user_id: str, content: str, ttl=3600):
    timestamp = int(time.time())
    token = f"{user_id}|{timestamp + ttl}|broadcast"
    message_id = secrets.token_hex(8)

    return f"""TYPE: POST
USER_ID: {user_id}
CONTENT: {content}
TTL: {ttl}
MESSAGE_ID: {message_id}
TOKEN: {token}

"""

def  handle_post(message: dict, peer_table, logger=None):
    user_id = message.get("USER_ID")
    content = message.get("CONTENT")
    display_name = peer_table.get_display_name(user_id)

    name_to_show = display_name if display_name is not None else user_id
    print(f"{name_to_show}:{content}")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received POST:\n{message}")
