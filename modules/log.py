import logging

logger: logging.Logger = logging.getLogger("discord")

logging.basicConfig(
        filename = "logs/full_bot_log.txt",
        format = "%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt = "%H:%M:%S",
        level = logging.INFO,
    )
