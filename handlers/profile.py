def build_profile_message(user_id: str, display_name: str, status: str) -> str:
    return f"""TYPE: PROFILE
USER_ID: {user_id}
DISPLAY_NAME: {display_name}
STATUS: {status}

"""

def handle_PROFILE(message: dict, sender_ip: str, peer_table, logger=None):
    user_id = message.get("USER_ID")
    name = message.get("DISPLAY_NAME")
    status = message.get("STATUS")
    peer_table.update_peer(user_id, sender_ip, name=name, status=status)
    print(f"Discovered peer: {name} - {status}")

    if logger and logger.verbose:
        profile_str = build_profile_message(user_id, name, status).strip()
        logger.debug(f"[VERBOSE LOG] Received PROFILE from {sender_ip}:\n{profile_str}")