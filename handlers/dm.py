# TODO: Implement DM (Direct Message) handler
#
# This function should handle incoming TYPE: DM messages.
# see RFC for detailed info
#
# Expected fields:
# - TYPE: DM
# - FROM: <string>            # Sender's user_id (e.g., username@ipaddress)
# - TO: <string>              # Receiver's user_id 
# - CONTENT: <string>         
# - TIMESTAMP: 
# - MESSAGE_ID: <string>      # Unique ID 
# - TOKEN: <string>           # Format: user_id|timestamp|chat (hardcoded for now)
#
# NOTE: use (if logger and logger.verbose:) for conditional verbose logging
# add your commands in commands.py and call handlers in dispatcher.py

import time
import secrets

def build_dm_message(sender_id: str, receiver_id: str, content: str, ttl=3600):
    timestamp = int(time.time())
    expires = timestamp + ttl
    token = f"{sender_id}|{expires}|chat"
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
    content = message.get("CONTENT")

    display_name = peer_table.get(sender_id)

    name_to_show = display_name if display_name is not None else sender_id
    print(f"{name_to_show}: {content}")

    if logger and logger.verbose:
        logger.debug(f"[VERBOSE LOG] Received DM\n{message}")
