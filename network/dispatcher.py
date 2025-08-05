from handlers import profile, ping, post, file_transfer, post, dm, follow, like, group
from utils.parser import parse_message
from network.sender import send_message


def dispatch_message(message: str, sender_ip: str, user_profile):
    peer_table = user_profile["peer_table"]
    logger = user_profile["logger"]
    msg_dict = parse_message(message)
    msg_type = msg_dict.get("TYPE")

    from_field = msg_dict.get("FROM") or msg_dict.get("USER_ID", "")
    claimed_ip = from_field.split("@")[-1] if "@" in from_field else None

    # Safety Considerations
    # SAFE_TYPES = {"PING", "PROFILE"}
    # if msg_type not in SAFE_TYPES:
    #    if claimed_ip != sender_ip:
    #        warning = f"[SECURITY] Claimed IP ({claimed_ip}) ≠ sender IP ({sender_ip})"
    #        if logger:
    #            logger.warning(warning)
    #        else:
    #            print(warning)
    #        return

    if msg_type == "PROFILE":
        profile.handle_PROFILE(msg_dict, sender_ip, peer_table, logger)
    elif msg_type == "PING":
        ping.handle_PING(msg_dict, sender_ip, peer_table, logger)
    elif msg_type == "POST":
        post.handle_post(msg_dict, peer_table, user_profile, logger)
    elif msg_type == "DM":
        dm.handle_dm(msg_dict, peer_table, logger)
    elif msg_type == "FOLLOW":
        follow.handle_follow(msg_dict, peer_table, logger)
    elif msg_type == "UNFOLLOW":
        follow.handle_unfollow(msg_dict, peer_table, logger)
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
    elif msg_type == "LIKE":
        like.handle_like(msg_dict, peer_table, user_profile, logger)
    elif msg_type == "GROUP_CREATE":
        group.handle_group_create(msg_dict, sender_ip, user_profile, send_message)
    elif msg_type == "GROUP_UPDATE":
        group.handle_group_update(msg_dict, sender_ip, user_profile, send_message)
    elif msg_type == "GROUP_MESSAGE":
        group.handle_group_message(msg_dict, sender_ip, user_profile, send_message)
    elif msg_type == "GROUP_INFO_RESPONSE":
        group.handle_group_info(msg_dict, sender_ip, user_profile, send_message)

    else:
        print(f"[DISPATCH] Unknown message type: {msg_type}")
