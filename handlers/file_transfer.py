import base64
from network.sender import send_message
from tokens.validator import validate_token
from utils.formatter import format_message

# Track incoming file chunks by filename
incoming_files = {}  

# Maximum chunk size for file transfers
CHUNK_SIZE = 1000  

# Message Builder Functions
def build_file_offer(from_id, to_id, filename, filesize, total_chunks, token):
    return {
        "TYPE": "FILE_OFFER",
        "FROM": from_id,
        "TO": to_id,
        "FILENAME": filename,
        "FILESIZE": str(filesize),
        "CHUNKS": str(total_chunks),
        "TOKEN": token,
    }

def build_file_chunk(from_id, to_id, filename, chunk_index, chunk_total, data, token):
    return {
        "TYPE": "FILE_CHUNK",
        "FROM": from_id,
        "TO": to_id,
        "FILENAME": filename,
        "CHUNK_INDEX": str(chunk_index),
        "CHUNK_TOTAL": str(chunk_total),
        "DATA": base64.b64encode(data).decode('utf-8'),
        "TOKEN": token,
    }

def build_file_received(from_id, to_id, filename, token):
    return {
        "TYPE": "FILE_RECEIVED",
        "FROM": from_id,
        "TO": to_id,
        "FILENAME": filename,
        "STATUS": "SUCCESS",
        "TOKEN": token,
    }

def handle_file_offer(msg, peer_table, logger):
    filename = msg["FILENAME"]
    total_chunks = int(msg["CHUNKS"])
    incoming_files[filename] = {
        "chunks": [None] * total_chunks,
        "received": 0,
        "total": total_chunks,
    }
    logger.info(f"[FILE_OFFER] Ready to receive {filename} ({total_chunks} chunks)")

def handle_file_chunk(msg, peer_table, logger, send_func):
    token = msg.get("TOKEN")
    if not validate_token(token, expected_scope="file"):
        logger.warn(f"[FILE_OFFER] Invalid token from {msg.get('FROM')}")
        return
    
    filename = msg["FILENAME"]
    chunk_index = int(msg["CHUNK_INDEX"])
    data = base64.b64decode(msg["DATA"])

    if filename not in incoming_files:
        logger.warning(f"[FILE_CHUNK] Received chunk for unknown file: {filename}")
        return

    file = incoming_files[filename]
    file["chunks"][chunk_index] = data
    file["received"] += 1

    if file["received"] == file["total"]:
        save_path = f"received_{filename}"
        with open(f"received_{filename}", "wb") as f:
            for chunk in file["chunks"]:
                f.write(chunk)

        logger.success(f"[FILE_RECEIVED] {filename} saved to {save_path}.")
        response = build_file_received(msg["TO"], msg["FROM"], filename, msg["TOKEN"])
        to_ip = msg["FROM"].split("@")[1]
        send_func(format_message(response), to_ip)

        del incoming_files[filename]

def handle_file_received(msg, peer_table, logger):
    logger.success(f"[RECEIVED CONFIRMATION] {msg['FILENAME']} transfer completed!")