import os
from utils.formatter import format_message
from handlers.file_transfer import build_file_offer, build_file_chunk
from network.sender import send_message

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
        pass
    elif command == "/dm":
        pass
    elif command == "/follow":
        pass
    elif command == "/unfollow":
        pass
    # 
    # add your commands
    #
    elif command == "/sendfile":
        handle_sendfile_command(args, user_profile)
    elif command == "/help":
        handle_help_command()
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
        print(f"Profile updated: name='{user_profile['username']}' status='{user_profile['status']}'")
        if "profile_updated" in user_profile:
            user_profile["profile_updated"].set()
    else:
        print("Usage: /profile name=\"Your Name\" status=\"Your status\"")


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
    print("  /profile name=\"Your Name\" status=\"Your status\"")
    print("  /status  Exploring LSNP!")    
    print("  /sendfile <user@ip> <file_path>")
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
    
    token = user_profile.get("token", "")
    if "file" not in token:
        print("Token does not include 'file' scope.")
        return

    with open(file_path, "rb") as f:
        file_data = f.read()

    chunk_size = 1000  
    chunks = [file_data[i:i + chunk_size] for i in range(0, len(file_data), chunk_size)]
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