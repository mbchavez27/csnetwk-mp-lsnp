import base64
import os
from utils.formatter import format_message
from handlers.file_transfer import build_file_offer, build_file_chunk
from network.sender import send_message
from tokens.tokens_utils import get_valid_token
from tokens.generator import generate_token
from handlers.follow import build_follow_message, build_unfollow_message
from handlers.dm import build_dm_message
from handlers.post import build_post_message
from handlers.like import build_like_message
from network.sender import unicast_message, broadcast_message
from tokens.validator import revoke_token
from handlers.tictactoe import (sendInvite, sendMove, sendResults, active_games, findIP, printBoard, checkWinner)
import time
import random
from handlers.tictactoe import (sendInvite, sendMove, sendResults, active_games, findIP, printBoard, checkWinner)
import time
import random

def handle_user_command(input_str, user_profile, peer_table):
    """
    Dispatches a command based on user input.
    """
    if not input_str.startswith("/"):
        print("Invalid command. Use `/help` for available commands.")
        return

    tokens = input_str.strip().split()
    command = tokens[0].lower()
    args = tokens[1:]

    if command == "/profile":
        handle_profile_command(args, user_profile)
    elif command == "/status":
        handle_status_command(args, user_profile)
    elif command == "/verbose":
        handle_verbose_command(args, user_profile)
    elif command == "/post":
        handle_post_command(args, user_profile)
    elif command == "/dm":
        handle_dm_command(args, user_profile)
    elif command == "/follow":
        handle_follow_command(args, user_profile)
    elif command == "/unfollow":
        handle_unfollow_command(args, user_profile)
    elif command == "/like":
        handle_like_command(args, user_profile)
    elif command == "/sendfile":
        handle_sendfile_command(args, user_profile)
    
    elif command == "/help":
        handle_help_command()
    elif command == "/group_create":
        handle_group_create_command(args, user_profile)
    elif command == "/group_update":
        handle_group_update_command(args, user_profile)
    elif command == "/group_msg":
        handle_group_message_command(args, user_profile)
    elif command == "/peer_info":
        handle_info_command(user_profile)
    elif command == "/tictactoe":
        handle_tictactoe_command(args, user_profile, peer_table)
    elif command == "/move":
        handle_move_command(args, user_profile, peer_table)
    elif command == "/exit":
        handle_exit_command(user_profile)
    else:
        print(f"Unknown command: {command}. Type `/help` for available commands.")


def handle_profile_command(args, user_profile):
    updated = False
    for arg in args:
        if arg.startswith("name="):
            new_name = arg.split("=", 1)[1].strip('"')
            user_profile["username"] = new_name
            updated = True
        elif arg.startswith("status="):
            new_status = arg.split("=", 1)[1].strip('"')
            user_profile["status"] = new_status
            updated = True

    if updated:
        print(
            f"Profile updated: name='{user_profile['username']}' status='{user_profile['status']}'"
        )
        if "profile_updated" in user_profile:
            user_profile["profile_updated"].set()
    else:
        print('Usage: /profile name="Your Name" status="Your status"')


def handle_status_command(args, context):
    if not args:
        print("Usage: /status Feeling happy!")
        return
    new_status = " ".join(args)
    context["status"] = new_status
    print(f"Status updated to: '{new_status}'")
    if "profile_updated" in context:
        context["profile_updated"].set()


def handle_verbose_command(args, user_profile):
    if not args:
        print("Usage: /verbose on|off")
        return

    mode = args[0].lower()
    if "logger" not in user_profile:
        print("Logger not found in context.")
        return

    if mode == "on":
        user_profile["logger"].verbose = True
        print("Verbose mode ON")
    elif mode == "off":
        user_profile["logger"].verbose = False
        print("Verbose mode OFF")
    else:
        print("Invalid option. Use /verbose on|off")


def handle_help_command():
    print("Available commands:")
    print('  /profile name="Your Name" status="Your status"')
    print("  /status  Exploring LSNP!")
    print("  /verbose <on|off>")
    print("  /post <message>")
    print("  /dm <user@ip> <message>")
    print("  /follow <user@ip>")
    print("  /unfollow <user@ip>")
    print("  /like <user@ip> <post_timestamp>")
    print("  /sendfile <user@ip> <file_path>")
    print("  /group_create <group_name> <member1@ip> <member2@ip> ...")
    print("  /group_update <group_name> <add|remove> <member@ip> ...")
    print("  /group_msg <group_name> <message>")
    print("  /tictactoe @username")
    print("  /move <gameid> <position>")
    print("  /help")
    print("  /info")
    print("  /exit")


def handle_sendfile_command(args, user_profile):
    if len(args) != 2:
        print("Usage: /sendfile <user@ip> <file_path>")
        return

    to_id = args[0]
    file_path = args[1]

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    token = get_valid_token("file", user_profile)

    with open(file_path, "rb") as f:
        file_data = f.read()

    chunk_size = 1000
    chunks = [
        file_data[i : i + chunk_size] for i in range(0, len(file_data), chunk_size)
    ]
    total_chunks = len(chunks)
    filename = os.path.basename(file_path)
    to_ip = to_id.split("@")[1]

    offer_msg = build_file_offer(
        from_id=user_profile["user_id"],
        to_id=to_id,
        filename=filename,
        filesize=len(file_data),
        total_chunks=total_chunks,
        token=token,
    )
    send_message(format_message(offer_msg), to_ip)
    user_profile["logger"].send(offer_msg, to_ip)

    for i, chunk in enumerate(chunks):
        chunk_msg = build_file_chunk(
            from_id=user_profile["user_id"],
            to_id=to_id,
            filename=filename,
            chunk_index=i,
            chunk_total=total_chunks,
            data=chunk,
            token=token,
        )
        send_message(format_message(chunk_msg), to_ip)
        user_profile["logger"].send(chunk_msg, to_ip)

    print(f"File '{filename}' sent to {to_id} in {total_chunks} chunks.")


def handle_post_command(args, user_profile):
    if not args:
        print("Usage: /post <message>")
        return

    content = " ".join(args)
    token = get_valid_token("broadcast", user_profile)
    user_id = user_profile["user_id"]

    message_str = build_post_message(user_id, content, token)

    msg_dict = {}
    for line in message_str.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            msg_dict[key.strip()] = value.strip()

    key = (msg_dict["USER_ID"], int(msg_dict["TIMESTAMP"]))
    user_profile["recent_posts"][key] = msg_dict["CONTENT"]

    broadcast_message(message_str, user_profile["ip"])


def handle_follow_command(args, user_profile):
    if not args:
        print("Usage: /follow <user@ip>")
        return

    receiver_id = args[0]
    sender_id = user_profile["user_id"]
    token = get_valid_token("follow", user_profile)
    message = build_follow_message(sender_id, receiver_id, token)

    target_user = user_profile["peer_table"].get_peer(receiver_id)
    if not target_user:
        print(f"User {receiver_id} not found.")
        return

    unicast_message(message, target_user["ip"])
    user_profile["peer_table"].follow(receiver_id)
    print(f"You followed {receiver_id}")


def handle_unfollow_command(args, user_profile):
    if not args:
        print("Usage: /unfollow <user@ip>")
        return

    receiver_id = args[0]
    sender_id = user_profile["user_id"]
    token = get_valid_token("follow", user_profile)
    message = build_unfollow_message(sender_id, receiver_id, token)

    target_user = user_profile["peer_table"].get_peer(receiver_id)
    if not target_user:
        print(f"User {receiver_id} not found.")
        return

    unicast_message(message, target_user["ip"])
    user_profile["peer_table"].unfollow(receiver_id)
    print(f"You unfollowed {receiver_id}")


def handle_dm_command(args, user_profile):
    if len(args) < 2:
        print("Usage: /dm <user@ip> <message>")
        return

    receiver_id = args[0]
    message_content = " ".join(args[1:])
    token = get_valid_token("chat", user_profile)
    sender_id = user_profile["user_id"]

    peer = user_profile["peer_table"].get_peer(receiver_id)
    if not peer:
        print(f"Unknown peer: {receiver_id}")
        return

    message = build_dm_message(sender_id, receiver_id, message_content, token)
    unicast_message(message, peer["ip"])
    print(f"DM sent to {receiver_id}")


def handle_like_command(args, user_profile):
    if len(args) != 2:
        print("Usage: /like <user@ip> <post_timestamp>")
        return

    receiver_id, ts_str = args
    try:
        post_timestamp = int(ts_str)
    except ValueError:
        print("Invalid timestamp.")
        return

    key = (receiver_id, post_timestamp)
    liked_posts = user_profile.setdefault("liked_posts", set())

    # Determine action: LIKE or UNLIKE
    if key in liked_posts:
        action = "UNLIKE"
        liked_posts.remove(key)
    else:
        action = "LIKE"
        liked_posts.add(key)

    token = get_valid_token("broadcast", user_profile)
    message = build_like_message(
        user_profile["user_id"],
        receiver_id,
        post_timestamp,
        action,
        token,
    )

    to_ip = receiver_id.split("@")[1]
    send_message(message, to_ip)

    action_verb = "liked" if action == "LIKE" else "unliked"
    print(f"You {action_verb} {receiver_id.split('@')[0]}'s post from {post_timestamp}")


def handle_group_create_command(args, user_profile):
    if len(args) < 2:
        print("Usage: /group_create <group_name> <member1@ip> <member2@ip> ...")
        return

    group_name = args[0]
    input_members = [m.strip() for arg in args[1:] for m in arg.split(",") if m.strip()]
    from_id = user_profile["user_id"]
    # to ensure creator is part of the members list
    members = list(set(input_members + [from_id]))
    token = get_valid_token("group", user_profile)

    local_groups = user_profile.setdefault("groups", {})
    local_groups[group_name] = {
        "creator": from_id, 
        "members": members
    }

    msg = {
        "TYPE": "GROUP_CREATE",
        "GROUP_NAME": group_name,
        "MEMBERS": ",".join(members),
        "FROM": from_id,
        "TOKEN": token,
    }

    msg_str = format_message(msg)

    for peer in members:
        try:
            name, ip = peer.split("@")
            user_profile["logger"].send(msg_str, ip)
            send_message(msg_str, ip)
        except ValueError:
            print(f"Invalid member format: {peer} (should be name@ip)")


def handle_group_update_command(args, user_profile):
    if len(args) < 3:
        print("Usage: /group_update <group_name> <add|remove> <member@ip> ...")
        return

    group_name = args[0]
    action = args[1].upper()
    members = args[2:]
    from_id = user_profile["user_id"]
    token = get_valid_token("group", user_profile)

    if action not in ("ADD", "REMOVE"):
        print("Invalid action. Use 'add' or 'remove'")
        return

    local_groups = user_profile.setdefault("groups", {})
    group = local_groups.get(group_name)

    if not group:
        print(f"[GROUP_UPDATE] Group '{group_name}' does not exist.")
        return
    
    msg = {
        "TYPE": "GROUP_UPDATE",
        "GROUP_NAME": group_name,
        "ACTION": action,
        "MEMBERS": ",".join(members),
        "FROM": from_id,
        "TOKEN": token,
    }

    # Send to all current group members (including the ones being removed)
    all_targets = set(group["members"])
    all_targets.add(from_id)
    
    for member in all_targets:
        if member == from_id:
            continue
        ip = member.split("@")[1]
        send_message(format_message(msg), ip)
        user_profile["logger"].send(msg, ip)

    # Update local group info
    if action == "ADD":
        for m in members:
            if m not in group["members"]:
                group["members"].append(m)
    elif action == "REMOVE":
        group["members"] = [m for m in group["members"] if m not in members]

    print(
        f"[GROUP_UPDATE] Group '{group_name}' updated ({action}): {', '.join(members)}"
    )


def handle_group_message_command(args, user_profile):
    if len(args) < 2:
        print("Usage: /group_msg <group_name> <message>")
        return

    group_name = args[0]
    content = " ".join(args[1:])
    from_id = user_profile["user_id"]
    token = get_valid_token("group", user_profile)

    local_groups = user_profile.setdefault("groups", {})
    group_info = local_groups.get(group_name)

    if not group_info:
        print(f"[ERROR] Group '{group_name}' not found.")
        return

    msg = {
        "TYPE": "GROUP_MESSAGE",
        "GROUP_NAME": group_name,
        "FROM": from_id,
        "MESSAGE": base64.b64encode(content.encode()).decode(),
        "TOKEN": token,
        "ID": generate_token(user_profile["user_id"], 60, "group_msg"),
    }

    for member in group_info["members"]:
        if member == from_id:
            continue
        ip = member.split("@")[1]
        send_message(format_message(msg), ip)
        user_profile["logger"].send(msg, ip)

    print(f"[GROUP_MESSAGE] Sent to group '{group_name}': {content}")

def handle_info_command(user_profile):
    peer_table = user_profile["peer_table"]

    print("\n=== PEER INFO ===")
    print(f"User ID   : {user_profile['user_id']}")
    print(f"Username  : {user_profile['username']}")
    print(f"Status    : {user_profile['status']}")
    print(f"IP        : {user_profile['ip']}")

    print("\nPeers:")
    for uid, info in peer_table.all_peers().items():
        name = info.get("name", uid.split("@")[0])
        status = info.get("status", "No status")
        print(f"{uid} | {name} | {status}")

    print("\nFollowing:")
    for f in sorted(peer_table.following):
        print(f)

    print("\nFollowers:")
    for f in sorted(peer_table.followers):
        print(f)

    print("\nRecent Posts:")
    for (uid, ts), content in user_profile["recent_posts"].items():
        print(f"{uid} at {ts}: {content}")

    print("\nGroups:")
    groups = user_profile.get("groups", {})
    if not groups:
        print("Not a member of any groups")
    else:
        for group_name, group_data in groups.items():
            members = group_data.get("members", [])
            print(f"{group_name} | Members: {', '.join(members)}")

    print("====================\n")

def handle_tictactoe_command(args, user_profile, peer_table):
    if len(args) < 1:
            print("tictactoe @username")
            return
        
    opponent_username = args[0].lstrip("@")
    opponent_ip = None
    for user_id, peer in peer_table.peers.items():
        if user_id.startswith(opponent_username + "@"):
            opponent_ip = peer.get("ip")
            break

    if not opponent_ip:
        print(f"Could not find user {opponent_username}.")
        return
        
    symbol_choice = input("Choose between X or O [X/O]: ").strip().upper()
    if symbol_choice not in ["X", "O"]:
        print("Invalid choice. Randomly picking between X or O.")
        symbol_choice = random.choice(["X", "O"])
        
    game_id = f"g{int(time.time())}"
    sendInvite(game_id, symbol_choice, opponent_ip, user_profile, peer_table)
    print(f"Game ID: {game_id}")

        
def handle_move_command(args, user_profile, peer_table):
    
    if len(args) < 2:
        print("move GAMEID POSITION")
        return
    game_id = args[0]
    try:
        position = int(args[1])
    except ValueError:
        print("Position must be a number (0-8).")
        return
        
    if position < 0 or position > 8:
        print("Invalid number. Use 0-8.")
        return
        
    game = active_games.get(game_id)
    if not game:
        print(f"No active game found with ID {game_id}")
        return
        
    opponent_ip = findIP(game, user_profile["user_id"])
    if not opponent_ip:
        print("Could not find user.")
        return
        
    matches = [s for s, uid in game["players"].items() if uid == user_profile["user_id"]]
    user_symbol = matches[0]
    sendMove(game_id, position, user_symbol, opponent_ip, user_profile, peer_table)
 
    if game["board"][position] == " ":
        game["board"][position] = user_symbol
        printBoard(game["board"])
    else:
        print("Position already taken.")


def handle_exit_command(user_profile):
    # Revoke tokens
    for token in user_profile.get("tokens", {}).values():
        revoke_token(token)

    print("All tokens revoked. Exiting...")
    exit(0)
