import logging


def get_logger(
        name, log_file='', level=logging.INFO,
        fmt='%(asctime)s:%(name)s:%(levelname)s:%(message)s', types='stream'
):
    """
    Generate logger

    Args:
        name: logger name
        log_file: logger file
        level: level of logs - debug, info, error
        fmt: log formats
        types: file or stream, or both

    Returns:
        logger

    Examples:
        >>> get_logger(name='download_data', level='debug', types='stream')
        >>> get_logger(name='preprocess', log_file='pre.log', types='file|stream')
    """
    if isinstance(level, str): level = getattr(logging, level.upper())
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)

    if not len(logger.handlers):
        formatter = logging.Formatter(fmt=fmt)

        if 'file' in types:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(fmt=formatter)
            logger.addHandler(file_handler)

        if 'stream' in types:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(fmt=formatter)
            logger.addHandler(stream_handler)

    return logger
