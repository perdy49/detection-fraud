import logging
import os


def setup_logger():

    os.makedirs(
        "results",
        exist_ok=True
    )

    logger = logging.getLogger(
        "fraud_detection"
    )

    logger.setLevel(
        logging.INFO
    )

    if not logger.handlers:

        file_handler = logging.FileHandler(
            "results/training.log"
        )

        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        file_handler.setFormatter(
            formatter
        )

        console_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            file_handler
        )

        logger.addHandler(
            console_handler
        )

    return logger