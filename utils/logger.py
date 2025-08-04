import datetime
from utils.formatter import format_message


class Logger:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def send(self, message, target):
        if isinstance(message, dict):
            message = format_message(message)
        if self.verbose:
            print(f"[{self._timestamp()}] SEND > {target}:\n{message.strip()}\n")

    def recv(self, message, sender_ip):
        if self.verbose:
            if isinstance(message, dict):
                message = format_message(message)
        print(f"[{self._timestamp()}] RECV < {sender_ip}:\n{message.strip()}\n")

    def info(self, msg):
        if self.verbose:
            print(f"[{self._timestamp()}] INFO: {msg}")

    def _timestamp(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def success(self, msg):
        if self.verbose:
            print(f"[{self._timestamp()}] SUCCESS: {msg}")

    def warning(self, msg):
        if self.verbose:
            print(f"[{self._timestamp()}] WARNING: {msg}")

    def debug(self, msg):
        if self.verbose:
            print(f"[{self._timestamp()}] {msg}")
