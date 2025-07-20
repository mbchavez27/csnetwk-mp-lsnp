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