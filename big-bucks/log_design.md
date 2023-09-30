## Log Design
- In the log_design.md file, include the following information:
  Where to record event data
  We will record the event data in a log file named application.log in the application root folder.
  Which events to log
  We will log the following events:
  1.User login attempts
  2.User registration attempts
  3.Accessing home page
  4.Accessing admin holdings
  5.Accessing admin orders
  6.Accessing admin profile form
  7.Accessing admin profile with POST method
  8.Errors during database queries
  9.Event attributes
  10.User logout 
  11. Alvant Data download
  12. home data get info

  For each log entry, we will include the following attributes:
  ## Timestamp
  1.Log level (e.g., INFO, WARNING, ERROR)
  2.Module name
  3.Log message
  4.Implementation
  Create a logger with a custom log format that includes the timestamp, log level, module name, and log message.
  Configure the logger to write the logs to application.log in the application root folder.
  In each event to be logged, use the logger to create a log entry with the appropriate log level and message, and include the module name and event details in the log message.
  Ensure that the logger is properly initialized and used in all the necessary application files.
  Now, the log entries in application.log should provide a clear and useful record of the application's events, including login, registration, and symbol-related events, following the guidelines in the 'cheat sheet'.

   ## Set Log

~~~python
import logging

class CustomLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        func_name = self.extra.get("func_name", "Unknown Function")
        return f"[Function: {func_name}] {msg}", kwargs

def setup_global_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z"
    )

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


~~~

