def parse_message(raw_message: str):
    lines = raw_message.strip().split('\n')
    msg = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            msg[key.strip()] = value.strip()
    return msg