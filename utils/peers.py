import time

class PeerTable:
    def __init__(self, timeout=300):
        self.peers = {}  
        self.timeout = timeout

    def update_peer(self, user_id, ip, name=None, status=None):
        """Add or update a peer's info and last_seen time."""
        peer = self.peers.get(user_id, {})
        peer["ip"] = ip
        peer["last_seen"] = time.time()
        if name:
            peer["name"] = name
        if status:
            peer["status"] = status
        self.peers[user_id] = peer

    def mark_seen(self, user_id):
        """Refresh last_seen for a peer (e.g., from PING)."""
        if user_id in self.peers:
            self.peers[user_id]["last_seen"] = time.time()

    def is_active(self, user_id):
        """Check if peer is currently considered active."""
        peer = self.peers.get(user_id)
        if not peer:
            return False
        return (time.time() - peer["last_seen"]) <= self.timeout

    def remove_stale_peers(self):
        """Delete peers that haven't been seen recently."""
        now = time.time()
        to_remove = [uid for uid, p in self.peers.items() if now - p["last_seen"] > self.timeout]
        for uid in to_remove:
            del self.peers[uid]
            print(f"[INFO] Removed inactive peer: {uid}")

    def get_peer(self, user_id):
        """Get peer info dictionary."""
        return self.peers.get(user_id)

    def get_name(self, user_id):
        """Return display name or fallback to user_id."""
        peer = self.peers.get(user_id)
        return peer["name"] if peer and "name" in peer else user_id

    def all_peers(self):
        """Return all known peers."""
        return self.peers
