import argparse
import threading
import time

from network.sender import broadcast_message
from network.receiver import listen_for_messages
from network.dispatcher import dispatch_message
from handlers.profile import build_profile_message
from handlers.ping import build_ping_message
from handlers.commands import handle_user_command
from utils.logger import Logger
from utils.ip import get_own_ip
from utils.peers import PeerTable
from tokens.generator import generate_token

peer_table = PeerTable()
BROADCAST_INTERVAL = 300 
PORT = 50999

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default=get_own_ip(), help="The simulated peer IP (e.g., 127.0.0.2)") # for testing on own terminals for now
    parser.add_argument("--username", required=True)
    parser.add_argument("--status", default="Exploring LSNP!")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    logger = Logger(verbose=args.verbose)
    ip = args.ip
    user_id = f"{args.username}@{ip}"

    user_profile = {
        "username": args.username,
        "status": args.status,
        "ip": ip,
        "user_id": user_id,
        "logger": logger,
    }

    last_profile_time = 0

    # User Discovery: PING or PROFILE at regular 300-second intervals using broadcast communication
    def user_discovery():
        nonlocal last_profile_time
        while True:
            now = time.time()
            if now - last_profile_time >= BROADCAST_INTERVAL:
                msg = build_profile_message(
                    user_id,
                    user_profile["username"],
                    user_profile["status"],
                )
                last_profile_time = now
            else:
                msg = build_ping_message(user_id)
            
            broadcast_message(msg, ip)
            logger.send(msg, "<broadcast>")
            time.sleep(BROADCAST_INTERVAL) 

    def interactive_input():
        while True:
            try:
                user_input = input("> ")
                handle_user_command(user_input, user_profile)
            except (EOFError, KeyboardInterrupt):
                break

    def on_receive(msg, addr):
        if addr[0] == ip:
            return  # Ignore own broadcast
        logger.recv(msg, addr[0])
        dispatch_message(msg, addr[0], peer_table, logger)

    threading.Thread(target=user_discovery, daemon=True).start()
    threading.Thread(target=interactive_input, daemon=True).start()

    listen_for_messages(on_receive, ip)

if __name__ == "__main__":
    main()