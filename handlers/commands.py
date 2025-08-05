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


def handle_user_command(input_str, user_profile):
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
    elif command == "/info":
        handle_group_info_command(args, user_profile)
    else:
        print(f"Unknown command: {command}. Type `/help` for available commands.")


def handle_profile_command(args, user_profile):
    """
    Updates display name and/or status.
    """
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
    """
    Quickly updates just the status.
    """
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
    print("  /sendfile <user@ip> <file_path>")
    print("  /group_create <group_name> <member1@ip> ...")
    print("  /group_update <group_name> <add|remove> <user@ip> ...")
    print("  /group_msg <group_name> <message>")
    print("  /info <group_name>")
    print("  /help")


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
    """
    SENDS A FOLLOW MESSAGE TO THE USER.
    """
    if not args:
        print("Usage: /follow <user_id>")
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
    """
    SENDS AN UNFOLLOW MESSAGE TO THE USER.
    """
    if not args:
        print("Usage: /unfollow <user_id>")
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
    """
    SENDS A DM
    """
    if len(args) < 2:
        print("Usage: /dm <user_id> <message>")
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
        print("Usage: /group_create <group_name> <member1@ip1> <member2@ip2> ...")
        return

    group_name = args[0]
    members = [m.strip() for arg in args[1:] for m in arg.split(",") if m.strip()]
    from_id = user_profile["user_id"]
    token = user_profile.get("token", "default_token")

    local_groups = user_profile.setdefault("groups", {})
    local_groups[group_name] = {"members": members}

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
        print("Usage: /group_update <group_name> <add|remove> <user@ip> ...")
        return

    group_name = args[0]
    action = args[1].upper()
    members = args[2:]
    from_id = user_profile["user_id"]
    token = get_valid_token("group", user_profile)

    if action not in ("ADD", "REMOVE"):
        print("Invalid action. Use 'add' or 'remove'")
        return

    msg = {
        "TYPE": "GROUP_UPDATE",
        "GROUP_NAME": group_name,
        "ACTION": action,
        "MEMBERS": ",".join(members),
        "FROM": from_id,
        "TOKEN": token,
    }

    for member in members:
        ip = member.split("@")[1]
        send_message(format_message(msg), ip)
        user_profile["logger"].send(msg, ip)

    # Update local group info
    local_groups = user_profile.setdefault("groups", {})
    if group_name in local_groups:
        if action == "ADD":
            for m in members:
                if m not in local_groups[group_name]["members"]:
                    local_groups[group_name]["members"].append(m)
        elif action == "REMOVE":
            local_groups[group_name]["members"] = [
                m for m in local_groups[group_name]["members"] if m not in members
            ]

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


def handle_group_info_command(args, user_profile):
    """
    Sends a request to retrieve group information.
    Usage: /info <group_name>
    """
    if len(args) != 1:
        print("Usage: /info <group_name>")
        return

    group_name = args[0]
    from_id = user_profile["user_id"]
    token = get_valid_token("group", user_profile)

    msg = {
        "TYPE": "GROUP_INFO",
        "GROUP_NAME": group_name,
        "FROM": from_id,
        "TOKEN": token,
    }

    # Send to all group members if group exists locally, else broadcast
    local_groups = user_profile.get("groups", {})
    group = local_groups.get(group_name)

    if group:
        for member in group.get("members", []):
            if member == from_id:
                continue
            try:
                _, ip = member.split("@")
                send_message(format_message(msg), ip)
                user_profile["logger"].send(msg, ip)
            except Exception as e:
                print(f"[ERROR] Failed to send group info request to {member}: {e}")
    else:
        # Fallback: broadcast to network
        print(f"[INFO] Group '{group_name}' not found locally. Broadcasting request.")
        broadcast_message(format_message(msg), user_profile["ip"])

    print(f"[INFO] Group info request sent for '{group_name}'.")
