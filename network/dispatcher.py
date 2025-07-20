from handlers import profile, ping, post
from utils.parser import parse_message

def dispatch_message(message: str, sender_ip: str, peer_table=None, logger=None):
    msg_dict = parse_message(message)
    msg_type = msg_dict.get("TYPE")

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
        pass
    elif msg_type == "FILE_CHUNK":
        pass
    elif msg_type == "FILE_RECEIVED":
        pass
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