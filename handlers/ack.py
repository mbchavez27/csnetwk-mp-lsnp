from network.sender import unicast_message

def send_ack(message_id: str, recipient_ip: str, port=50999):
    ack_msg = (
        f"TYPE: ACK\n"
        f"MESSAGE_ID: {message_id}\n"
        f"STATUS: RECEIVED\n"
    )
    unicast_message(ack_msg, recipient_ip, port)