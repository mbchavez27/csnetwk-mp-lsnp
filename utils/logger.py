import datetime

class Logger:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def send(self, message, target):
        if self.verbose:
            print(f"[{self._timestamp()}] SEND > {target}:\n{message.strip()}\n")

    def recv(self, message, sender_ip):
        if self.verbose:
            print(f"[{self._timestamp()}] RECV < {sender_ip}:\n{message.strip()}\n")

    def info(self, msg):
        if self.verbose:
            print(f"[{self._timestamp()}] INFO: {msg}")

    def _timestamp(self):
        return datetime.datetime.now().strftime("%H:%M:%S")
    
    def debug(self, msg):
        if self.verbose:
            print(f"[{self._timestamp()}] {msg}")