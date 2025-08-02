from handlers import profile, ping, post
from utils.parser import parse_message

def dispatch_message(message: str, sender_ip: str, peer_table=None, logger=None):
    msg_dict = parse_message(message)
    msg_type = msg_dict.get("TYPE")

    from_field = msg_dict.get("FROM") or msg_dict.get("USER_ID", "")
    claimed_ip = from_field.split("@")[-1] if "@" in from_field else None

    # Safety Considerations
    SAFE_TYPES = {"PING", "PROFILE"}
    if msg_type not in SAFE_TYPES:
        if claimed_ip != sender_ip:
            warning = f"[SECURITY] Claimed IP ({claimed_ip}) ≠ sender IP ({sender_ip})"
            if logger:
                logger.warning(warning)
            else:
                print(warning)
            return
        
    if msg_type == "PROFILE":
        profile.handle_PROFILE(msg_dict, sender_ip, peer_table, logger)
    elif msg_type == "PING":
        ping.handle_PING(msg_dict, sender_ip, peer_table, logger)
    elif msg_type == "POST":
        pass
    elif msg_type == "DM":
        pass
    elif msg_type == "FOLLOW":
        pass
    elif msg_type == "UNFOLLOW":
        pass
    elif msg_type == "FILE_OFFER":
        file_transfer.handle_file_offer(msg_dict, peer_table, logger)
    elif msg_type == "FILE_CHUNK":
        file_transfer.handle_file_chunk(msg_dict, peer_table, logger, send_message)
    elif msg_type == "FILE_RECEIVED":
        file_transfer.handle_file_received(msg_dict, peer_table, logger)
    elif msg_type == "TICTACTOE_INVITE":
        pass
    elif msg_type == "TICTACTOE_MOVE":
        pass
    elif msg_type == "TICTACTOE_RESULT":
        pass
    elif msg_type == "GROUP_CREATE":
        pass
    elif msg_type == "GROUP_UPDATE":
        pass
    elif msg_type == "GROUP_MESSAGE":
        pass
    else:
        print(f"[DISPATCH] Unknown message type: {msg_type}")