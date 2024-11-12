import logging

# logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("server.log"), logging.StreamHandler()],
)


def get_logger(name):
    """
    Returns a logger instance with the given name.

    Parameters:
        name (str): Name to identify the logger.

    Returns:
        logging.Logger: Configured logger instance to track events, errors, and debug information
                        throughout the program.
    """
    return logging.getLogger(name)
