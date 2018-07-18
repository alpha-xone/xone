import logging


def get_logger(
        log_file, name, level=logging.INFO,
        fmt='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
        types='file;stream'
):

    if isinstance(level, str): level = getattr(logging, level.upper())
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)

    formatter = logging.Formatter(fmt=fmt)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(fmt=formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt=formatter)

    if not len(logger.handlers):
        if 'file' in types: logger.addHandler(file_handler)
        if 'stream' in types: logger.addHandler(stream_handler)

    return logger
