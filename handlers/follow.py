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