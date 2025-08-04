# TODO: Implement group message handlers in group.py
# see RFC for detailed info
# This module should handle the following message types:
#
# 1. GROUP_CREATE
# 2. GROUP_UPDATE
# 3. GROUP_MESSAGE
#
# NOTE: use (if logger and logger.verbose:) for conditional verbose logging
#     : tokens can be hardcoded for now
# add your commands in commands.py and call handlers in dispatcher.py
# handlers/group.py
import base64
from utils.serializer import serialize_message
from tokens.generator import generate_token
from utils.formatter import format_message
from network.sender import send_message


def handle_group_create(msg_dict, sender_ip, user_profile, send_message):
    logger = user_profile.get("logger")
    group_name = msg_dict.get("GROUP_NAME")
    from_user = msg_dict.get("FROM")
    members = msg_dict.get("MEMBERS", "").split(",")
    sender_username = user_profile.get("username")
    sender_id = f"{sender_username}@{sender_ip}"

    if not group_name or not from_user:
        return

    group_table = user_profile.setdefault("groups", {})
    if group_name in group_table:
        if logger and logger.verbose:
            logger.debug(f"[GROUP_CREATE] Group '{group_name}' already exists.")
        return

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
            "TOKEN": generate_token(sender_id, 3600, "group"),
        }
        _, target_ip = member.split("@")
        send_message(serialize_message(message), target_ip)


def handle_group_update(msg_dict, sender_ip, user_profile, send_message):
    logger = user_profile.get("logger")
    group_name = msg_dict.get("GROUP_NAME")
    action = msg_dict.get("ACTION")
    from_user = msg_dict.get("FROM")
    members = msg_dict.get("MEMBERS", "").split(",")

    group_table = user_profile.get("groups", {})
    group = group_table.get(group_name)

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

    for peer in group["members"]:
        msg = {
            "TYPE": "GROUP_UPDATE",
            "FROM": from_user,
            "GROUP_NAME": group_name,
            "ACTION": action,
            "MEMBERS": ",".join(members),
        }
        _, ip = peer.split("@")
        send_message(serialize_message(msg), ip)


def handle_group_message(msg_dict, sender_ip, user_profile, send_message):
    logger = user_profile.get("logger")
    group_name = msg_dict.get("GROUP_NAME")
    message = msg_dict.get("MESSAGE")
    from_user = msg_dict.get("FROM")

    group_table = user_profile.get("groups", {})
    group = group_table.get(group_name)

    if not group:
        if logger and logger.verbose:
            logger.debug(f"[GROUP_MESSAGE] Group '{group_name}' does not exist.")
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

    for peer in group["members"]:
        if peer == from_user:
            continue
        _, ip = peer.split("@")
        send_message(
            serialize_message(
                {
                    "TYPE": "GROUP_MESSAGE",
                    "FROM": from_user,
                    "GROUP_NAME": group_name,
                    "MESSAGE": message,
                }
            ),
            ip,
        )
