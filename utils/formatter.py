def format_message(msg: dict) -> str:
    return '\n'.join(f"{k}:{v}" for k, v in msg.items()) + '\n\n'