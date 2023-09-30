import logging


class CustomLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        func_name = self.extra.get("func_name", "Unknown Function")
        return f"[Function: {func_name}] {msg}", kwargs


def setup_global_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    # # 添加一个StreamHandler以将日志输出到控制台
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(
    #     logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"))

    logger = logging.getLogger()
    # logger.addHandler(console_handler)

    # 设置日志文件处理器
    file_handler = logging.FileHandler('application.log', mode='a')
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"))
    logger.addHandler(file_handler)


def get_logger(func_name):
    logger = logging.getLogger(func_name)
    return CustomLoggerAdapter(logger, {"func_name": func_name})


def log_event(logger, message, level=logging.INFO):
    if level == logging.INFO:
        logger.info(message)
    elif level == logging.WARNING:
        logger.warning(message)
    elif level == logging.ERROR:
        logger.error(message)
    elif level == logging.CRITICAL:
        logger.critical(message)
