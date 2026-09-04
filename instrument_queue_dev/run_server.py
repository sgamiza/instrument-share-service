import os
import sys

# for linux
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import instrument_queue_dev


# TODO 删除 py文件
if __name__ == '__main__':


    import logging
    logger = logging.getLogger()
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return the root logger.
    """
    logger.setLevel(logging.INFO)

    instrument_queue_dev.run_server() # 客户端是本机
    # instrument_queue_dev.run_server("YOUR_HOST")  # windows/linux server; client is remote
    # instrument_queue_dev.run_server_linux("127.0.0.1")  # linux 服务器
