def build_ping_message(user_id: str) -> str:
    return f"""TYPE: PING
USER_ID: {user_id}

"""

def handle_PING(message: dict, sender_ip: str, peer_table, logger=None):
    user_id = message.get("USER_ID")
    if logger and logger.verbose:
        ping_str = build_ping_message(user_id).strip()
        logger.debug(f"[VERBOSE LOG] Received PING from {sender_ip}:\n{ping_str}")
    else:
        pass