def serialize_message(msg_dict):
    lines = []
    for key, value in msg_dict.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines) + "\n\n"
