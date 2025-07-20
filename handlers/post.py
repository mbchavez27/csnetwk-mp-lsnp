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