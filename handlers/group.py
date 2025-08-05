import base64
from utils.serializer import serialize_message
from tokens.validator import validate_token

def handle_group_create(msg_dict, sender_ip, user_profile, send_message):
    logger = user_profile.get("logger")
    token = msg_dict.get("TOKEN")
    group_name = msg_dict.get("GROUP_NAME")
    from_user = msg_dict.get("FROM")
    members = msg_dict.get("MEMBERS", "").split(",")
    sender_username = user_profile.get("username")
    sender_id = f"{sender_username}@{sender_ip}"

    if not group_name or not from_user:
        return

    if not validate_token(token, expected_scope="group"):
        if logger:
            logger.warning(f"[GROUP_CREATE] Invalid token from {sender_id}")
        return
    
    group_table = user_profile.setdefault("groups", {})
    if group_name in group_table:
        if logger and logger.verbose:
            logger.debug(f"[GROUP_CREATE] Group '{group_name}' already exists.")
        return

    if sender_id != from_user:
        print(f"You've been added to {group_name}")

    all_members = list(set(members + [from_user]))
    group_table[group_name] = {"creator": from_user, "members": all_members}

    if logger and logger.verbose:
        logger.debug(
            f"[GROUP_CREATE] Group '{group_name}' created by {from_user} with members: {all_members}"
        )

    for member in all_members:
        if member == from_user:
            continue
        message = {
            "TYPE": "GROUP_CREATE",
            "GROUP_NAME": group_name,
            "FROM": sender_id,
            "TO": member,
            "TOKEN": token,
        }
        _, target_ip = member.split("@")
        send_message(serialize_message(message), target_ip)


def handle_group_update(msg_dict, sender_ip, user_profile, send_message):
    logger = user_profile.get("logger")
    token = msg_dict.get("TOKEN")
    group_name = msg_dict.get("GROUP_NAME")
    action = msg_dict.get("ACTION")
    from_user = msg_dict.get("FROM")
    msg_id = msg_dict.get("ID") or msg_dict.get("TOKEN")
    members = msg_dict.get("MEMBERS", "").split(",")

    # Recursion prevention using msg_id
    seen = user_profile.setdefault("user_seen_tokens", set())
    if msg_id in seen:
        return
    seen.add(msg_id)

    # Optional cleanup to limit memory
    if len(seen) > 1000:
        seen.clear()

    group_table = user_profile.get("groups", {})
    group = group_table.get(group_name)

    if not validate_token(token, expected_scope="group"):
        if logger:
            logger.warning(f"[GROUP_UPDATE] Invalid token from {from_user}")
        return
    
    if not group or group["creator"] != from_user:
        if logger and logger.verbose:
            logger.debug(f"[GROUP_UPDATE] Unauthorized or missing group: {group_name}")
        return

    if action == "ADD":
        for m in members:
            if m not in group["members"]:
                group["members"].append(m)
    elif action == "REMOVE":
        group["members"] = [m for m in group["members"] if m not in members]
    else:
        if logger and logger.verbose:
            logger.debug(
                f"[GROUP_UPDATE] Invalid action '{action}' for group '{group_name}'"
            )
        return

    if logger and logger.verbose:
        logger.debug(
            f"[GROUP_UPDATE] {action} members {members} in group '{group_name}'"
        )

    print(f'The group "{group_name}" member list was updated.')
    
    if from_user != user_profile["user_id"]:
        return  # Don't rebroadcast if not the creator

    for peer in group["members"]:
        msg = {
            "TYPE": "GROUP_UPDATE",
            "FROM": from_user,
            "GROUP_NAME": group_name,
            "ACTION": action,
            "MEMBERS": ",".join(members),
            "TOKEN": token,
        }
        _, ip = peer.split("@")
        send_message(
            serialize_message(
                {
                    "TYPE": "GROUP_UPDATE",
                    "FROM": from_user,
                    "GROUP_NAME": group_name,
                    "ACTION": action,
                    "MEMBERS": ",".join(members),
                    "ID": msg_id,
                }
            ),
            ip,
        )


def handle_group_message(msg_dict, sender_ip, user_profile, send_message):
    logger = user_profile.get("logger")
    token = msg_dict.get("TOKEN")
    group_name = msg_dict.get("GROUP_NAME")
    message = msg_dict.get("MESSAGE")
    from_user = msg_dict.get("FROM")
    msg_id = msg_dict.get("ID") or msg_dict.get("TOKEN")

    if not validate_token(token, expected_scope="group"):
        if logger:
            logger.warning(f"[GROUP_MESSAGE] Invalid token from {from_user}")
        return
    
    seen = user_profile.setdefault("user_seen_tokens", set())
    if msg_id in seen:
        return
    seen.add(msg_id)

    if len(seen) > 1000:
        seen.clear()

    group_table = user_profile.get("groups", {})
    group = group_table.get(group_name)

    if not group:
        if logger and logger.verbose:
            logger.debug(f"[GROUP_MESSAGE] Group '{group_name}' does not exist.")
        return

    receiver_id = user_profile["user_id"]
    if receiver_id not in group["members"]:
        if logger and logger.verbose:
            logger.debug(
                f"[GROUP_MESSAGE] Receiver '{receiver_id}' is not a member of group '{group_name}', ignoring message."
            )
        return
    
    if from_user not in group["members"]:
        if logger and logger.verbose:
            logger.debug(
                f"[GROUP_MESSAGE] Unauthorized sender '{from_user}' for group '{group_name}'."
            )
        return

    if logger and logger.verbose:
        try:
            decoded = base64.b64decode(message).decode()
        except Exception:
            decoded = "[invalid base64]"
        logger.debug(f"[GROUP_MESSAGE] {from_user} → {group_name}: {decoded}")

    try:
        decoded = base64.b64decode(message).decode()
    except Exception:
        decoded = "[invalid base64]"

    print(f"[{group_name}] {from_user.split('@')[0]}: {decoded}")

    for peer in group["members"]:
        if peer == from_user or peer == user_profile["user_id"]:
            continue
        _, ip = peer.split("@")
        send_message(
            serialize_message(
                {
                    "TYPE": "GROUP_MESSAGE",
                    "FROM": from_user,
                    "GROUP_NAME": group_name,
                    "MESSAGE": message,
                    "ID": msg_id,
                    "TOKEN": token,
                }
            ),
            ip,
        )


def handle_group_info(msg_dict, sender_ip, user_profile, send_message):
    logger = user_profile.get("logger")
    group_name = msg_dict.get("GROUP_NAME")
    from_user = msg_dict.get("FROM")

    group_table = user_profile.get("groups", {})
    group = group_table.get(group_name)

    if not group:
        if logger and logger.verbose:
            logger.debug(f"[GROUP_INFO] Group '{group_name}' not found.")
        return

    creator = group.get("creator", "[unknown]")
    members = group.get("members", [])

    if logger and logger.verbose:
        logger.debug(
            f"[GROUP_INFO] Sending group info for '{group_name}' to {from_user}"
        )

    response = {
        "TYPE": "GROUP_INFO_RESPONSE",
        "GROUP_NAME": group_name,
        "CREATOR": creator,
        "MEMBERS": ",".join(members),
    }

    try:
        _, ip = from_user.split("@")
        send_message(serialize_message(response), ip)
    except Exception as e:
        if logger:
            logger.warning(f"[GROUP_INFO] Failed to send info: {e}")
