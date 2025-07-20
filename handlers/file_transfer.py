# TODO: Implement file transfer handlers in file_transfer.py
# see RFC for detailed info
#
# This module should handle the following message types:
#
# 1. FILE_OFFER
# 2. FILE_CHUNK
# 3. FILE_RECEIVED
#
# NOTE: use (if logger and logger.verbose:) for conditional verbose logging
#     : tokens can be hardcoded for now
# add your commands in commands.py and call handlers in dispatcher.py