import os, sys, logging, datetime
from logging.handlers import TimedRotatingFileHandler

def setup_logger():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%H:%M:%S')

    handler = TimedRotatingFileHandler("logs/noDoot.log", when="midnight", interval=1, encoding="UTF-8")
    handler.suffix = "%Y%m%d"
    handler.setFormatter(formatter)

    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)

    logger = logging.getLogger("noDoot")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(screen_handler)

async def log(message, bot, level="INFO", debug=""):
    logChannel = bot.get_channel(int(os.getenv('log')))
    time = datetime.datetime.now().strftime('%H:%M:%S')

    if level == "ERROR":
        levelemote = "❌"
    elif level == "CRITICAL":
        levelemote = "🔥"
    elif level == "WARNING":
        levelemote = "❗"
    elif level == "DEBUG":
        levelemote = "🔧"
    else:
        levelemote = "🔎"

    await logChannel.send("`[" + time + "]` **" + levelemote + " " + level + ":** " + message)

    if debug == "":
        logDebug(message, level)
        return
    logDebug(debug, level)

def logDebug(message, level="INFO"):
    logger = logging.getLogger("noDoot")

    if level == "DEBUG":
        logger.debug(message)
    elif level == "CRITICAL":
        logger.critical(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    else:
        logger.info(message)