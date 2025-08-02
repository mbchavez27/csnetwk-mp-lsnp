import socket

def listen_for_messages(callback, ip='0.0.0.0', port=50999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((ip, port))
    except OSError as e:
        print(f"[RECEIVER ERROR] {e}")
        return

    print(f"[RECEIVER] Listening on {ip}:{port}...")

    try:
        while True:
            data, addr = sock.recvfrom(65535)
            callback(data.decode(), addr)
    except KeyboardInterrupt:
        print("\n[INFO] Stopped listening (Keyboard Interrupt). Exiting.")
    finally:
        sock.close()
