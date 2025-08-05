from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser
import socket

class LsnpMDNS:
    def __init__(self, user_id, port, on_peer_discovered):
        self.user_id = user_id
        self.port = port
        self.zeroconf = Zeroconf()
        self.on_peer_discovered = on_peer_discovered

    def register_service(self):
        ip_bytes = socket.inet_aton(self.get_local_ip())
        info = ServiceInfo(
            "_lsnp._udp.local.",
            f"{self.user_id}._lsnp._udp.local.",
            addresses=[ip_bytes],
            port=self.port,
            properties={},
            server=f"{self.user_id}.local.",
        )
        self.zeroconf.register_service(info)

    def browse_services(self):
        ServiceBrowser(self.zeroconf, "_lsnp._udp.local.", self)

    def remove_service(self, zeroconf, type_, name):
        pass

    def update_service(self, zeroconf, type_, name):
        # Not handling updates for now
        pass

    def add_service(self, zeroconf, type_, name):
        info = zeroconf.get_service_info(type_, name)
        if info and info.addresses:
            ip = socket.inet_ntoa(info.addresses[0])
            self.on_peer_discovered(ip)

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip