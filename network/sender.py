import socket

def broadcast_message(message: str, ip: str, port=50999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((ip, 0))  # bind to simulated local IP
    sock.sendto(message.encode(), ('<broadcast>', port))
    sock.close()

def unicast_message(message: str, ip: str, port=50999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (ip, port))