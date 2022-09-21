import logging, logging.handlers

ch = None

def init(name):
    global ch
    if name == "":
        name = "Root"
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if ch is None:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter("%(name)s - %(levelname)s: %(message)s")
        ch.setFormatter(formatter)
    
    if not logger.hasHandlers():
        logger.addHandler(ch)

    return logger