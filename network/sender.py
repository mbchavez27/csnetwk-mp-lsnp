import socket

def send_message(message: str, target_ip: str, local_ip: str = None, port: int = 50999, broadcast: bool = False):
    """
    Sends a message over UDP to a given IP.
    
    Args:
        message (str): The message to send. Should include \n\n termination.
        target_ip (str): The IP to send to. Use '<broadcast>' for broadcast.
        local_ip (str): Required if broadcast is True, to bind to simulated IP.
        port (int): The target port.
        broadcast (bool): Whether to send via broadcast.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if broadcast:
        if local_ip is None:
            raise ValueError("local_ip must be provided when broadcasting.")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind((local_ip, 0))  # Required for simulated broadcast IP

    if not message.endswith("\n\n"):
        message += "\n\n"

    sock.sendto(message.encode("utf-8"), (target_ip, port))
    sock.close()

def broadcast_message(message: str, ip: str, port=50999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((ip, 0))  # bind to simulated local IP
    sock.sendto(message.encode(), ('<broadcast>', port))
    sock.close()

def unicast_message(message: str, ip: str, port=50999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (ip, port))