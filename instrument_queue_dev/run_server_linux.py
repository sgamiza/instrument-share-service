import os
import sys

# for linux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import instrument_queue_dev

if __name__ == '__main__':

    # import logging
    # logger = logging.getLogger()
    # logger.setLevel(logging.INFO)

    instrument_queue_dev.run_server_linux("127.0.0.1")
